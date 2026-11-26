#!/usr/bin/env python3

import shutil
import subprocess
import tempfile
from pathlib import Path

from loguru import logger
from step.load_game_info import get_launcher
from util import lang
from util import state_file as state
from util import variables as var
from util.checksum import compare_checksum
from util.download import download
from util.heroic.find_library import get_data as get_heroic_data
from util.wine import protontricks, winetricks

default_tricks = [
    "win10",
    "arial",
    "fontsmooth=rgb",
]

yes = ("", "y", "yes")

vcrun_dlls = [
    "concrt140",
    "msvcp140",
    "msvcp140_1",
    "msvcp140_2",
    "msvcp140_atomic_wait",
    "msvcp140_codecvt_ids",
    "vcamp140",
    "vccorlib140",
    "vcomp140",
    "vcruntime140",
    "vcruntime140_1",
]
# The x86 redistributable does not ship these.
vcrun_x64_only_dlls = {"vcruntime140_1"}
vcredist_arches = (("x86", "vcredist_x86"), ("x64", "vcredist_x64"))
# File name suffix used for each architecture inside the redistributable's cabinets.
vcredist_cab_suffix = {"x86": "_x86", "x64": "_amd64"}
# Header tags Wine writes at offset 0x40 of its own DLLs (same check Proton uses).
wine_dll_tags = (b"Wine placeholder DLL", b"Wine builtin DLL")


def get_default_tricks() -> list[str]:
    return list(default_tricks)


def load_prefix() -> Path:
    """
    Determines the game's wine prefix, based on the relevant launcher.

    Returns
    -------
    Path
        The path to the game's wine prefix.
    """

    logger.debug("Loading game prefix based on launcher information.")
    prefix = None
    launcher = (
        get_launcher()
        if not state.current_instance
        else state.current_instance.launcher
    )
    match launcher:
        case "steam":
            logger.trace("Attempting to retrieve Steam prefix using protontricks.")
            prefix = protontricks.get_prefix(var.game_info.launcher_ids.steam)
        case "gog":
            logger.trace("Attempting to retrieve GOG prefix using heroic data.")
            data = get_heroic_data()
            prefix = data[3]
            if isinstance(prefix, dict):
                prefix = prefix.get("gog")
        case "epic":
            logger.trace("Attempting to retrieve Epic prefix using heroic data.")
            data = get_heroic_data()
            prefix = data[3]
            if isinstance(prefix, dict):
                prefix = prefix.get("epic")
        case _:
            logger.critical(
                f"Unrecognized launcher '{launcher}'. Unable to determine prefix path."
            )
            logger.critical(
                "This should not happen. Please report this issue to the developer."
            )
            raise SystemExit(1)

    if prefix is None:
        logger.critical(
            "Failed to determine prefix path from launcher data. Please ensure you've set up your prefix properly and have run the game at least once."
        )
        raise SystemExit(1)
    elif isinstance(prefix, str):
        prefix = Path(prefix).expanduser().resolve()
    elif isinstance(prefix, Path):
        prefix = prefix.expanduser().resolve()
    logger.debug(f"Determined prefix path: {prefix}")
    var.prefix = prefix
    return prefix


def _run_vcredist_installer(installer_path: Path, app_id: int | None = None):
    try:
        if app_id is not None:
            protontricks.run(
                ["-c", f'wine "{installer_path}" /quiet /norestart', str(app_id)]
            )
        else:
            prefix = var.prefix
            winetricks_path = Path(
                shutil.which("winetricks")
                or Path.home() / ".cache" / "mo2-lint" / "downloads" / "winetricks"
            )
            winetricks.run(
                winetricks_path, prefix, [f"wine {installer_path} /quiet /norestart"]
            )
    except SystemExit:
        logger.info(
            "vcredist installer finished (exit code indicates reboot or already installed)."
        )


def _set_vcredist_overrides(app_id: int | None = None):
    """Set DLL overrides for all VC++ runtime libraries."""
    logger.info("Setting DLL overrides for VC++ runtime libraries...")
    if app_id is not None:
        for dll in vcrun_dlls:
            protontricks.run(
                [
                    "-c",
                    f'wine reg add "HKEY_CURRENT_USER\\Software\\Wine\\DllOverrides" /v {dll} /d native,builtin /f',
                    str(app_id),
                ]
            )
    else:
        prefix = var.prefix
        winetricks_path = Path(
            shutil.which("winetricks")
            or Path.home() / ".cache" / "mo2-lint" / "downloads" / "winetricks"
        )
        for dll in vcrun_dlls:
            winetricks.run(
                winetricks_path,
                prefix,
                [
                    f'reg add "HKEY_CURRENT_USER\\Software\\Wine\\DllOverrides" /v {dll} /d native,builtin /f'
                ],
            )


def _download_vcredist(arch: str, resource_key: str) -> Path | None:
    resource = getattr(var.resource_info, resource_key, None)
    if not resource or not resource.download_url:
        logger.error(f"No {resource_key} URL configured in resource_info.yml.")
        return None

    cache_dir = Path.home() / ".cache" / "mo2-lint" / "downloads" / "vcredist"
    cache_dir.mkdir(parents=True, exist_ok=True)
    cached = cache_dir / f"VC_redist.{arch}.exe"
    if (
        cached.exists()
        and resource.checksum
        and not compare_checksum(cached, resource.checksum)
    ):
        logger.warning(f"Discarding corrupt cached VC++ installer: {cached}")
        cached.unlink()
    logger.info(f"Downloading VC++ Redistributable ({arch})...")
    installer_path = download(
        resource.download_url,
        cache_dir,
        f"VC_redist.{arch}.exe",
        checksum=resource.checksum,
    )
    if not installer_path:
        logger.error(f"Failed to download vcredist {arch} installer.")
    return installer_path


def _system_dll_dir(prefix: Path, arch: str) -> Path | None:
    """
    Gets the directory Windows loads `arch` system DLLs from in the given prefix.

    Accepts a Proton compatdata directory (containing `pfx`) or a wine prefix.
    Returns None if the prefix has no such directory (e.g. x64 in a win32 prefix).
    """
    for drive_c in (prefix / "pfx" / "drive_c", prefix / "drive_c"):
        windows = drive_c / "windows"
        if not windows.is_dir():
            continue
        syswow64 = windows / "syswow64"
        if not syswow64.is_dir():
            # 32-bit prefix: system32 holds x86 DLLs and there is no x64.
            return windows / "system32" if arch == "x86" else None
        return syswow64 if arch == "x86" else windows / "system32"
    return None


def _is_wine_builtin(path: Path) -> bool:
    try:
        with path.open("rb") as file:
            file.seek(0x40)
            return file.read(20).startswith(wine_dll_tags)
    except OSError:
        return False


def _non_native_vcrun_dlls(system_dir: Path, arch: str) -> list[str]:
    """Lists VC++ runtime DLLs that are missing or still Wine's builtin copies."""
    expected = [
        dll for dll in vcrun_dlls if arch == "x64" or dll not in vcrun_x64_only_dlls
    ]
    return [
        dll
        for dll in expected
        if not (system_dir / f"{dll}.dll").is_file()
        or _is_wine_builtin(system_dir / f"{dll}.dll")
    ]


def _extract_vcrun_dlls(
    installer_path: Path, arch: str, system_dir: Path, dlls: list[str]
) -> list[str]:
    """
    Copies native VC++ runtime DLLs straight out of the redistributable.

    The redistributable's installer can leave Wine's builtin DLLs in place under
    Proton (see https://bugs.winehq.org/show_bug.cgi?id=57518), which stops
    Mod Organizer 2 from starting. The installer is a WiX bundle whose attached
    containers are cabinets holding the DLLs as `<name>.dll_<arch>`.

    Returns
    -------
    list[str]
        The DLLs that could not be replaced.
    """
    cabextract = shutil.which("cabextract")
    if not cabextract:
        logger.error("cabextract is not available; cannot extract VC++ DLLs.")
        return dlls

    suffix = vcredist_cab_suffix[arch]
    with tempfile.TemporaryDirectory(prefix="mo2-lint-vcredist-") as temp:
        containers = Path(temp) / "containers"
        staged = Path(temp) / "dlls"
        staged.mkdir()
        subprocess.run(
            [cabextract, "-q", "-d", str(containers), str(installer_path)],
            capture_output=True,
            check=False,
        )
        filters = [arg for dll in dlls for arg in ("-F", f"{dll}.dll{suffix}")]
        for container in sorted(containers.iterdir()) if containers.is_dir() else []:
            if container.is_file():
                # Non-cabinet payloads simply fail to extract; that is expected.
                subprocess.run(
                    [cabextract, "-q", "-d", str(staged), *filters, str(container)],
                    capture_output=True,
                    check=False,
                )

        remaining = []
        for dll in dlls:
            source = staged / f"{dll}.dll{suffix}"
            target = system_dir / f"{dll}.dll"
            if not source.is_file() or _is_wine_builtin(source):
                remaining.append(dll)
                continue
            try:
                # Proton may symlink builtins into the prefix; unlink so the copy
                # never writes through into the Proton installation itself.
                target.unlink(missing_ok=True)
                shutil.copyfile(source, target)
            except OSError as error:
                logger.error(f"Failed to copy {dll}.dll to {system_dir}: {error}")
                remaining.append(dll)
                continue
            logger.debug(f"Installed native {dll}.dll ({arch}) to {system_dir}")
        return remaining


def repair_vcredist_dlls(prefix: Path | None = None) -> bool:
    """
    Ensures the prefix uses native VC++ runtime DLLs, extracting them if needed.

    Parameters
    ----------
    prefix : Path, optional
        Proton compatdata directory or wine prefix. Defaults to `var.prefix`.

    Returns
    -------
    bool
        True if every VC++ runtime DLL is native (or there was nothing to check).
    """
    prefix = prefix or var.prefix
    if prefix is None:
        logger.warning("No prefix known; skipping VC++ runtime verification.")
        return True

    all_native = True
    for arch, resource_key in vcredist_arches:
        system_dir = _system_dll_dir(Path(prefix), arch)
        if system_dir is None:
            logger.debug(f"No {arch} system directory in {prefix}; skipping.")
            continue

        pending = _non_native_vcrun_dlls(system_dir, arch)
        if not pending:
            logger.debug(f"Native VC++ runtime ({arch}) verified in {system_dir}")
            continue

        logger.warning(
            f"VC++ runtime ({arch}) is missing or still using Wine builtins for: "
            f"{', '.join(pending)}. Extracting native DLLs directly..."
        )
        installer_path = _download_vcredist(arch, resource_key)
        remaining = (
            _extract_vcrun_dlls(installer_path, arch, system_dir, pending)
            if installer_path
            else pending
        )
        if remaining:
            all_native = False
            logger.error(
                f"Could not install native VC++ runtime ({arch}) DLLs: {', '.join(remaining)}. "
                "Mod Organizer 2 may fail to start."
            )
        else:
            logger.success(f"Native VC++ runtime ({arch}) installed to {system_dir}")

    if not all_native:
        steam_id = var.game_info.launcher_ids.steam if var.game_info else None
        hint = (
            f"protontricks {steam_id} vcrun2022" if steam_id else "winetricks vcrun2022"
        )
        logger.warning(f"As a workaround, try running: {hint}")
    return all_native


def install_vcredist():
    app_id = var.game_info.launcher_ids.steam if var.launcher == "steam" else None

    for arch, resource_key in vcredist_arches:
        installer_path = _download_vcredist(arch, resource_key)
        if installer_path:
            logger.info(f"Installing VC++ Redistributable ({arch})...")
            _run_vcredist_installer(installer_path, app_id)

    _set_vcredist_overrides(app_id)
    repair_vcredist_dlls()


def configure():
    """
    Run the necessary winetricks/protontricks for the selected game launcher.
    """
    tricks = get_default_tricks() + list(var.game_info.tricks)
    logger.debug(f"Configuring prefix with the following tricks: {tricks}")
    match var.launcher:
        case "steam":
            app_id = var.game_info.launcher_ids.steam
            protontricks.apply(app_id, tricks)
            install_vcredist()
            tweaks_path = Path(tempfile.gettempdir()) / "mo2-lint-tweaks.reg"
            if tweaks_path.exists():
                protontricks.import_registry(app_id, tweaks_path)
            else:
                logger.warning(f"Registry tweak file not found: {tweaks_path}")
        case "gog" | "epic":
            prefix = var.prefix
            winetricks.apply(prefix=prefix, tricks=tricks)
            install_vcredist()


def prompt(confirmed: bool | None = None):
    """
    Prompts the user to confirm their prefix is set up, then configures it.

    Parameters
    ----------
    confirmed : bool, optional
        The user's answer, if already asked elsewhere. If None, the user is prompted.
    """
    prefix = load_prefix()
    for suffix in ["users", "drive_c", "pfx"]:
        if prefix.name == suffix:
            prefix = prefix.parent
    var.prefix = prefix
    logger.trace(f"Resolved prefix path for prompting: {prefix}")

    if confirmed is None:
        confirmed = lang.prompt_prefix_init()
    if not confirmed:
        logger.warning(
            "User did not confirm prefix setup. No support will be provided if errors occur."
        )

    configure()
