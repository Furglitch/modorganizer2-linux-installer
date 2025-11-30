#!/usr/bin/env python3

from pathlib import Path
from loguru import logger

cache: Path = Path("~/.cache/mo2-lint").expanduser()
download_cache: Path = cache / "downloads"
extract_cache: Path = cache / "extracted"
scriptextender_download_dir: Path = download_cache / "script_extenders"
scriptextender_extract_dir: Path = extract_cache / "script_extenders"
scriptextender_nexus_dl = False
plugin_download_dir: Path = download_cache / "plugins"
plugin_extract_dir: Path = extract_cache / "plugins"

url: dict[str, str] = {}
download_dir: dict[str, Path] = {}
extract_dir: dict[str, Path] = {}


def scriptextender_get_info():
    import util.variables as var

    if var.launcher == "heroic":
        type = var.heroic_runner
    else:
        type = "steam"

    if (
        var.game_info.get("script_extender") is None
        or var.game_info.get("script_extender", {}).get(type) is None
    ):
        logger.warning(f"No Script Extender information available for {var.launcher}.")
        return

    var.scriptextender_version = (
        var.game_info.get("script_extender", {})
        .get(type, {})
        .get("resource", {})
        .get("version")
    )

    url = (
        var.game_info.get("script_extender", {})
        .get(type, {})
        .get("resource", {})
        .get("url")
    )
    mod_id = (
        var.game_info.get("script_extender", {})
        .get(type, {})
        .get("resource", {})
        .get("mod_id")
    )
    file_id = (
        var.game_info.get("script_extender", {})
        .get(type, {})
        .get("resource", {})
        .get("file_id")
    )
    checksum = (
        var.game_info.get("script_extender", {})
        .get(type, {})
        .get("resource", {})
        .get("checksum")
    )
    files = var.game_info.get("script_extender", {}).get(type, {}).get("files")

    if url:
        var.scriptextender_url = url
        logger.trace(f"Determined Script Extender URL: {var.scriptextender_url}")
    if mod_id and file_id:
        var.scriptextender_nxm_modid = mod_id
        var.scriptextender_nxm_fileid = file_id
        logger.trace(
            f"Determined Script Extender Nexus Mod ID: {var.scriptextender_nxm_modid} - File ID: {var.scriptextender_nxm_fileid}"
        )
    if not (url or (mod_id and file_id)):
        var.scriptextender_url = None
        var.scriptextender_nxm_modid = None
        var.scriptextender_nxm_fileid = None
        logger.warning(
            f"Unable to find Script Extender download URL or Nexus Mod IDs for {var.launcher}."
        )
    if checksum:
        var.scriptextender_checksum = checksum
        logger.trace(
            f"Determined Script Extender checksum: {var.scriptextender_checksum}"
        )
    if files:
        var.scriptextender_files = files
        logger.trace(
            f"Determined Script Extender file list: {var.scriptextender_files}"
        )


def scriptextender_path():
    from util.variables import (
        scriptextender_url,
        scriptextender_nxm_modid,
        scriptextender_nxm_fileid,
    )

    filename = None
    if scriptextender_url:
        filename = scriptextender_url.split("/")[-1]
        logger.trace(f"Determined Script Extender filename: {filename}")
    elif scriptextender_nxm_modid and scriptextender_nxm_fileid:
        global scriptextender_nexus_dl
        scriptextender_nexus_dl = True
        logger.error("NXM handling for Script Extender is not yet implemented.")
        pass  # TODO Implement NXM handling

    global scriptextender_download_dir, scriptextender_extract_dir
    scriptextender_download_dir = scriptextender_download_dir / filename
    scriptextender_extract_dir = scriptextender_extract_dir / Path(filename).stem
    scriptextender_download_dir.parent.mkdir(parents=True, exist_ok=True)
    scriptextender_extract_dir.mkdir(parents=True, exist_ok=True)
    logger.debug(
        f"Script Extender download path created: {scriptextender_download_dir.parent}"
    )
    logger.debug(f"Script Extender extract path created: {scriptextender_extract_dir}")


def scriptextender_download_url():
    from util.checksum import checksum_local
    from util.variables import scriptextender_checksum

    if scriptextender_download_dir.exists():
        if scriptextender_checksum:
            if checksum_local(scriptextender_download_dir, scriptextender_checksum):
                logger.debug(
                    f"Script Extender already downloaded and verified at: {scriptextender_download_dir}"
                )
                return
            else:
                logger.warning(
                    f"Checksum mismatch for existing Script Extender at: {scriptextender_download_dir}. Re-downloading."
                )
    from util.variables import scriptextender_url, scriptextender_version
    from urllib.request import urlretrieve

    logger.debug(
        f"Downloading Script Extender version {scriptextender_version} from {scriptextender_url}"
    )
    try:
        urlretrieve(scriptextender_url, scriptextender_download_dir)
        checksum_local(scriptextender_download_dir, scriptextender_checksum)
        logger.debug(f"Downloaded Script Extender to {scriptextender_download_dir}")
    except Exception as e:
        logger.error(f"Failed to download Script Extender: {e}")
        return


def scriptextender_download_nexus():  # TODO
    pass


def scriptextender_extract():
    from patoolib import extract_archive as unzip
    from util.variables import scriptextender_files

    if scriptextender_files:
        logger.trace(
            f"Verifying existing Script Extender files in {scriptextender_extract_dir}"
        )
        missing = []
        for rel in scriptextender_files:
            path = scriptextender_extract_dir / rel
            if not path.exists():
                missing.append(path)
                logger.trace(f"Missing Script Extender file: {path}")
        if not missing:
            logger.debug(
                f"All Script Extender files already exist in {scriptextender_extract_dir}; skipping extraction."
            )
            return

    try:
        unzip(str(scriptextender_download_dir), outdir=str(scriptextender_extract_dir))
        logger.debug(f"Extracted Script Extender to {scriptextender_extract_dir}")
    except Exception as e:
        logger.error(f"Failed to extract Script Extender: {e}")
        return


def scriptextender_install():
    from util.variables import game_install_path, scriptextender_files
    import shutil

    for file in scriptextender_files:
        file = Path(file)
        source = scriptextender_extract_dir / file
        destination = Path(game_install_path) / file.name
        if source.is_dir():
            shutil.copytree(source, destination, dirs_exist_ok=True)
            logger.trace(f"Copied Script Extender directory {source} to {destination}")
        elif source.is_file() and not destination.exists():
            shutil.copy(source, destination)
            logger.trace(f"Copied Script Extender file {source} to {destination}")
        else:
            logger.debug(
                f"Script Extender file {destination} already exists; skipping copy."
            )


def plugin_path():  # TODO
    pass


def plugin_download():  # TODO
    pass


def plugin_extract():  # TODO
    pass


def plugin_install():  # TODO
    pass


def resource_download(resource_name: str):
    from util.variables import load_resourceinfo

    load_resourceinfo()
    path(resource_name)
    download(resource_name)
    if not resource_name == "winetricks":
        extract(resource_name)
        install(resource_name)
    pass


def path(resource_name: str):
    from util.variables import resource_info

    url[resource_name] = resource_info.get(resource_name, {}).get("download_url")
    filename = url.get(resource_name).split("/")[-1]
    download_dir[resource_name] = _download_dir = download_cache / filename
    extract_dir[resource_name] = _extract_dir = extract_cache / Path(filename).stem
    _download_dir.parent.mkdir(parents=True, exist_ok=True)
    _extract_dir.mkdir(parents=True, exist_ok=True)
    logger.debug(
        f"{resource_name.replace('_', ' ').title()} download path created: {_download_dir.parent}"
    )
    logger.debug(
        f"{resource_name.replace('_', ' ').title()} extract path created: {_extract_dir}"
    )


def download(resource_name: str):
    from util.checksum import checksum_local
    from util.variables import resource_info

    _data = resource_info.get(resource_name)
    _dir = download_dir.get(resource_name)
    _url = url.get(resource_name)
    _name = resource_name.replace("_", " ").title()

    if _dir.exists():
        expected = _data.get("checksum")
        if expected:
            if checksum_local(_dir, expected):
                logger.debug(f"{_name} already downloaded and verified at: {_dir}")
                import stat

                _dir.chmod(
                    _dir.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
                )
                return
            else:
                logger.warning(
                    f"Checksum mismatch for existing {_name} at: {_dir}. Re-downloading."
                )

    attempts = 3
    for i in range(attempts):
        if i < attempts:
            logger.debug(f"Attempt {i + 1} to download {_name}.")
            logger.trace(f"Downloading from URL: {_url}")

            from urllib.request import urlretrieve

            try:
                urlretrieve(_url, _dir)
                checksum_local(_dir, _data.get("checksum"))
                logger.debug(f"Downloaded {_name} to {_dir}")
                if resource_name == "winetricks":
                    import stat

                    _dir.chmod(
                        _dir.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
                    )
                return
            except Exception as e:
                logger.error(f"Failed to download {_name}: {e}")
            break
    logger.error(f"Failed to download resource after {attempts} attempts.")
    return


def extract(resource_name: str):
    _download_dir = download_dir.get(resource_name)
    _extract_dir = extract_dir.get(resource_name)
    _name = resource_name.replace("_", " ").title()

    from patoolib import extract_archive as unzip

    if not check_existing(resource_name, _extract_dir):
        try:
            unzip(str(_download_dir), outdir=str(_extract_dir))
            logger.debug(f"Extracted {_name} to {_extract_dir}")
        except Exception as e:
            logger.error(f"Failed to extract {_name}: {e}")
            return


def check_existing(resource_name: str, dir: Path = None) -> bool:
    match resource_name:
        case "mod_organizer":
            name = "Mod Organizer"
            exe = Path("ModOrganizer.exe")
        case "java":
            name = "Java"
            exe = Path("bin") / "java.exe"
        case "winetricks":
            name = "winetricks"
            exe = Path("winetricks")
    exists = (dir / exe).exists()
    if exists:
        logger.trace(f"{name} exe found at: {dir}")
    return exists


def install(resource_name: str):
    _name = resource_name.replace("_", " ").title()
    _extract_dir = extract_dir.get(resource_name)

    match resource_name:
        case "mod_organizer":
            from util.variables import parameters

            dir = Path(parameters.get("directory"))
        case "java":
            from util.variables import prefix

            # prefix = Path("~/.cache/mo2-lint/test-output/prefix").expanduser()
            dir = (Path(prefix) / "drive_c" / "java").expanduser()
    dir.mkdir(parents=True, exist_ok=True)
    if check_existing(resource_name, dir):
        logger.debug(f"{_name} already installed at {dir}; skipping installation.")
        return
    else:
        try:
            import shutil

            logger.debug(f"Installing {_name} to {dir}...")
            shutil.copytree(_extract_dir, dir, dirs_exist_ok=True)
            logger.success(f"{_name} installed to {dir}.")
        except Exception as e:
            logger.error(f"Failed to install {_name}: {e}")
            return


def main():
    cache.mkdir(parents=True, exist_ok=True)
    logger.debug(f"Cache directory ensured at: {cache}")
    from util.variables import parameters, game_info, launcher

    if (
        parameters.get("script_extender") is True
        and game_info.get("script_extender").get(launcher) is not None
    ):
        scriptextender_get_info()
        scriptextender_path()
        scriptextender_download_url()
        scriptextender_extract()
    #    scriptextender_install()
    # if parameters.get("plugins"): # TODO
    #    plugin_path()
    #    plugin_download()
    #    plugin_extract()
    #    plugin_install()

    resource_download("mod_organizer")
    resource_download("winetricks")
    if parameters.get("game") == ("skyrim" or "enderal"):
        resource_download("java")
