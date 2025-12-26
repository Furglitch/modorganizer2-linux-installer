#!/usr/bin/env python3

from pathlib import Path
from loguru import logger

name: dict[str, str] = {}
url: dict[str, str] = {}
nexus_id: dict[str, tuple[str, int, int]] = {}
checksum: dict[str, str] = {}
files: dict[str, list] = {}
download_dir: dict[str, Path] = {}
extract_dir: dict[str, Path] = {}
cache_dir: Path = Path("~/.cache/mo2-lint").expanduser()

prompt_mod_organizer_update = """
It appears that Mod Organizer 2 is already installed in the target folder.
"""


def download_scriptextender():
    import util.variables as var

    if var.launcher == "heroic":
        se_entries = var.game_info.get("script_extender", {}).get(var.heroic_runner)
    else:
        se_entries = var.game_info.get("script_extender", {}).get("steam")
    if not se_entries:
        logger.debug("No script extender information available for this launcher.")
        return
    if isinstance(se_entries, dict):
        se_entries = [se_entries]
    logger.trace(f"Available script extender entries: {se_entries}")

    choice_index = 0
    if len(se_entries) > 1:
        print("Multiple script extender versions are available for this game:")
        for i, entry in enumerate(se_entries):
            ver = entry.get("version") or entry.get("name") or f"entry {i + 1}"
            runtime = entry.get("runtime")
            mod_id = entry.get("mod_id")
            file_id = entry.get("file_id")
            src = entry.get("url") or (
                f"nexus(mod={mod_id}, file={file_id})"
                if mod_id or file_id
                else "unknown"
            )
            if runtime:
                msg = f"{ver} for {runtime} - {src}"
            else:
                msg = f"{ver} - {src}"
            print(f"{i + 1}: {msg}")
        sel = input(
            f"Choose version [1-{len(se_entries)}] (default {len(se_entries)}): "
        ).strip()
        if sel.isdigit():
            idx = int(sel) - 1
            if 0 <= idx < len(se_entries):
                choice_index = idx
        else:
            choice_index = len(se_entries) - 1

    se_info = se_entries[choice_index]

    se = "scriptextender"
    name[se] = "Script Extender"
    url[se] = se_info.get("url")
    nexus_id[se] = (
        var.game_info.get("nexus_id"),
        se_info.get("mod_id"),
        se_info.get("file_id"),
    )
    checksum[se] = se_info.get("checksum")
    files[se] = se_info.get("files") or []

    logger.trace(
        f"Determined values for Script Extender: URL={url.get(se)}, Nexus IDs={nexus_id.get(se)}, Checksum={checksum.get(se)}, Files={files.get(se)}"
    )

    # Prefer direct URL if present, otherwise fall back to Nexus IDs when available
    if url.get(se):
        get_paths(se)
        download(se)
        extract(se)
        install(se)
    else:
        game_id, mod_id, file_id = nexus_id.get(se, (None, None, None))
        if game_id and mod_id and file_id:
            from util.nexus.download_mod import filename

            file = filename(game_id, mod_id, file_id)
            get_paths(se, file)
            download_nexus(se)
            extract(se)
            install(se)
        else:
            logger.error(
                "No valid download information for Script Extender; skipping installation."
            )


def download_resources():
    from util.variables import load_resourceinfo

    load_resourceinfo()
    from util.variables import parameters, resource_info as info

    for resource in (
        ("mod_organizer", "winetricks", "java")
        if parameters.get("game") == ("skyrim" or "enderal")
        else ("mod_organizer", "winetricks")
    ):
        name[resource] = resource.replace("_", " ").title()
        url[resource] = info.get(resource, {}).get("download_url")
        checksum[resource] = info.get(resource, {}).get("checksum")
        files[resource] = ["*"]
        get_paths(resource)
        download(resource)
        if not resource == "winetricks":
            extract(resource)
            install(resource)


def download_plugins(plugin: str):
    from util.variables import load_plugininfo

    info = load_plugininfo()
    manifest = {}
    for entry in info:
        if entry.get("Identifier") == plugin:
            manifest[plugin] = entry.get("Manifest")
            break

    from urllib.request import urlretrieve as dl

    file = Path(dl(manifest.get(plugin))[0])
    with open(file, "r") as f:
        from pydantic_core import from_json

        json = from_json(f.read())
        logger.trace(f"Downloaded plugin manifest for {plugin}: {json}")

    name[plugin] = json.get("Name")
    latest = json.get("Versions", [])[-1]
    files[plugin] = latest.get("PluginPath")
    url[plugin] = latest.get("DownloadUrl")
    checksum[plugin] = None

    get_paths(plugin)
    download(plugin)
    extract(plugin)
    install(plugin)


def check_existing(src: str, dir: Path) -> bool:
    match src:
        case "mod_organizer":
            return (dir / "ModOrganizer.exe").exists()
        case "winetricks":
            return (dir / "winetricks").exists()
        case "java":
            return (dir / "bin" / "java").exists()
        case "scriptextender":
            return any((dir / f).exists() for f in files.get(src, []))


def get_paths(src: str, filename: str = None):
    if not filename:
        filename = url.get(src).split("/")[-1]

    download_dir[src] = cache_dir / "downloads" / filename
    download_dir.get(src).parent.mkdir(parents=True, exist_ok=True)
    logger.debug(f"Download path for {src}: {download_dir.get(src)}")

    extract_dir[src] = cache_dir / "extracted" / Path(filename).stem
    extract_dir.get(src).mkdir(parents=True, exist_ok=True)
    logger.debug(f"Extraction path for {src}: {extract_dir.get(src)}")


def download(src: str):
    from util.checksum import checksum_local

    hash = checksum.get(src) if checksum.get(src) else None
    dir = download_dir.get(src)

    if hash is not None and dir.exists():
        logger.debug(f"{src} already downloaded at {dir}; ensuring validity.")
        if checksum_local(dir, hash):
            logger.debug(f"Checksum for {src} verified.")
            if src == "winetricks":
                import stat

                dir.chmod(dir.stat().st_mode | stat.S_IEXEC)
            return

    _name = name.get(src)
    _url = url.get(src)
    attempts = 3
    for i in range(attempts):
        logger.trace(f"Attempt {i + 1} to download {_name} from {_url}")
        from urllib.request import urlretrieve as dl

        try:
            dl(_url, dir)
            checksum_local(dir, hash)
            logger.debug(f"Downloaded {_name} to {dir} and verified checksum.")
            if src == "winetricks":
                import stat

                dir.chmod(dir.stat().st_mode | stat.S_IEXEC)
            return
        except Exception as e:
            logger.error(f"Failed to download {_name} on attempt {i + 1}: {e}")
    logger.error(f"Failed to download resource after {attempts} attempts.")


def download_nexus(src: str):
    from util.checksum import checksum_local

    hash = checksum.get(src) if checksum.get(src) else None
    dir = download_dir.get(src)

    if hash is not None and dir.exists():
        logger.debug(f"{src} already downloaded at {dir}; ensuring validity.")
        if checksum_local(dir, hash):
            logger.debug(f"Checksum for {src} verified.")
            return

    from util.nexus.download_mod import nexus_download

    game_id, mod_id, file_id = nexus_id.get(src, ("", 0, 0))
    nexus_download(game_id, str(mod_id), str(file_id), dir.parent)


def extract(src: str):
    if not check_existing(src, extract_dir.get(src)):
        try:
            from patoolib import extract_archive as unzip

            unzip(str(download_dir.get(src)), outdir=extract_dir.get(src))
            logger.debug(f"Extracted {name.get(src)} to {extract_dir.get(src)}")
        except Exception as e:
            logger.error(f"Failed to extract {name.get(src)}: {e}")


def install(src: str):
    _name = name.get(src)
    dir = None
    from util.variables import parameters

    match src:
        case "mod_organizer":
            dir = Path(parameters.get("directory")).expanduser()
        case "java":
            from util.variables import prefix

            dir = Path(prefix) / "drive_c" / "java".expanduser()
        case "scriptextender":
            from util.variables import game_install_path

            dir = Path(game_install_path).expanduser()
        case src if src in (parameters.get("plugins")):
            dir = (Path(parameters.get("directory")) / "plugins").expanduser()
    dir.mkdir(parents=True, exist_ok=True)

    if check_existing(src, dir):
        if not src == "mod_organizer":
            logger.debug(f"{_name} already installed at {dir}; skipping installation.")
            return
        else:
            logger.debug(
                f"{_name} already installed at {dir}; prompting for reinstallation."
            )
            print(prompt_mod_organizer_update)
            if input(
                "Would you like to update it? This will overwrite existing files. [y/N]: "
            ).strip().lower() not in ("", "y", "yes"):
                logger.info(f"Skipping reinstallation of {_name}.")
                return
    try:
        from shutil import copytree, copy2

        if (
            files[src] != "*"
            and files[src] != ["*"]
            and files[src] != []
            and files[src] is not None
        ):
            for file in files[src]:
                file = Path(file)
                source = extract_dir.get(src) / file
                destination = dir / file.name
                if not source.exists():
                    logger.warning(
                        f"Expected file {source} does not exist; aborting installation."
                    )
                    return
                elif source.is_dir():
                    copytree(source, destination, dirs_exist_ok=True)
                    logger.trace(f"Copied directory {source} to {destination}.")
                elif source.is_file() and not destination.exists():
                    copy2(source, destination)
                    logger.trace(f"Copied file {source} to {destination}.")
                else:
                    logger.warning(
                        f"Destination {destination} already exists; skipping copy of {source}."
                    )
        else:
            copytree(extract_dir.get(src), dir, dirs_exist_ok=True)
    except Exception as e:
        import traceback

        logger.error(f"Failed to install {_name}: {e}")
        logger.debug("Traceback:\n" + traceback.format_exc())
    logger.success(f"Installed {_name} to {dir}.")


def symlink_instance():
    from pathlib import Path
    from util.variables import parameters, game_info

    source = Path(parameters.get("directory")).expanduser()
    target = Path("~/.config/mo2-lint/instances").expanduser()
    target.mkdir(parents=True, exist_ok=True)
    link = target / game_info.get("nexus_id")

    if not source.exists():
        logger.warning(f"MO2 instance directory does not exist: {source}")
        return
    try:
        if link.exists() or link.is_symlink():
            if link.is_symlink() and link.resolve() == source.resolve():
                logger.debug(f"Symlink already correct at {link}")
                return
            elif link.is_symlink():
                link.unlink()
                logger.debug(f"Removed stale symlink at {link}")
            else:
                logger.warning(
                    f"Path exists, but is not a symlink. Please remove it manually: {link}"
                )
                return
        link.symlink_to(source)
        logger.success(f"Created symlink {link} -> {source}")
    except Exception as e:
        logger.error(f"Failed to create symlink {link} -> {source}: {e}")


def main():
    cache_dir.mkdir(parents=True, exist_ok=True)
    logger.debug(f"Cache directory ensured at {cache_dir}")
    from util.variables import parameters, game_info, launcher

    if (
        parameters.get("script_extender") is True
        and game_info.get("script_extender").get(launcher) is not None
    ):
        download_scriptextender()
    download_resources()
    if parameters.get("plugins"):
        for plugin in parameters.get("plugins"):
            download_plugins(plugin)
    symlink_instance()
