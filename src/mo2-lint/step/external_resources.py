#!/usr/bin/env python3

from pathlib import Path
from loguru import logger

cache: Path = Path("~/.cache/mo2-lint").expanduser()
download_cache: Path = cache / "downloads"
extract_cache: Path = cache / "extracted"
scriptextender_download_dir: Path = download_cache / "script_extenders"
scriptextender_extract_dir: Path = extract_cache / "script_extenders"
scriptextender_nexus_dl = False


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
    if scriptextender_download_dir.exists():
        from util.checksum import checksum_local
        from util.variables import scriptextender_checksum

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

    print(scriptextender_files)
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


def modorganizer_path():  # TODO
    pass


def modorganizer_download():  # TODO
    pass


def modorganizer_extract():  # TODO
    pass


def modorganizer_install():  # TODO
    pass


def java_path():  # TODO
    pass


def java_download():  # TODO
    pass


def java_extract():  # TODO
    pass


def java_install():  # TODO
    pass


def winetricks_path():  # TODO
    pass


def winetricks_download():  # TODO
    pass


def winetricks_extract():  # TODO
    pass


def winetricks_install():  # TODO
    pass


# ! To be fair, I think aside from scriptextender, most of these can use a singular extract and download function with parameters, rather than individual ones.
# ! Scriptextender is just special because of the file lists. Anyways, I'll cross that bridge when I get to it.


def main():
    cache.mkdir(parents=True, exist_ok=True)
    logger.debug(f"Cache directory ensured at: {cache}")
    from util.variables import parameters

    if parameters.get("script_extender") is True:
        scriptextender_get_info()
        scriptextender_path()
        scriptextender_download_url()
        scriptextender_extract()
        scriptextender_install()
    # if parameters.get("plugins"): # TODO
    #    plugin_path()
    #    plugin_download()
    #    plugin_extract()
    #    plugin_install()
    modorganizer_path()
    modorganizer_download()
    modorganizer_extract()
    modorganizer_install()
    java_path()
    java_download()
    java_extract()
    java_install()
    winetricks_path()
    winetricks_download()
    winetricks_extract()
    winetricks_install()
