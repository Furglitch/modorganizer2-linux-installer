#!/usr/bin/env python3

from loguru import logger
from pathlib import Path
from patoolib import extract_archive as unzip
from shutil import copytree, copyfile as copy, rmtree
from typing import Optional
from urllib.request import urlretrieve as request
from util import lang, variables as var, state_file as state
from util.checksum import compare_checksum
from util.download import download as dl, download_nexus as nexus_dl
from util.state_file import symlink_instance
import json

cache_dir: Path = Path("~/.cache/mo2-lint").expanduser()
download_dir = cache_dir / "downloads"
extract_dir = download_dir / "extracted"


def download_mod_organizer():
    """
    Runs the download and installation process for Mod Organizer 2.
    """
    logger.debug("Initiating Mod Organizer 2 download...")
    url = var.resource_info.mod_organizer.download_url
    checksum = var.resource_info.mod_organizer.checksum
    path_internal = var.resource_info.mod_organizer.path_internal
    checksum_internal = var.resource_info.mod_organizer.checksum_internal
    downloaded = dl(url, download_dir, checksum=checksum)
    extracted = extract(downloaded, extract_dir / downloaded.stem)
    if extracted and extracted.exists():
        destination = var.input_params.directory
        mo2_exec = destination / path_internal
        if (  # if ModOrganizer.exe exists in destination check if it's the same file
            destination.exists() and mo2_exec.exists()
        ):
            if not compare_checksum(mo2_exec, checksum_internal):
                if not lang.prompt_install_mo2_checksum_fail(str(mo2_exec)):
                    logger.info(
                        "User opted to not overwrite existing Mod Organizer 2 installation."
                    )
                    return
        elif not destination.exists():
            destination.mkdir(parents=True, exist_ok=True)
        install(extracted, destination, None)
        logger.debug(f"Mod Organizer 2 installed to {destination}")


def download_winetricks():
    """
    Runs the download process for Winetricks.
    """
    logger.debug("Initiating Winetricks download...")
    url = var.resource_info.winetricks.download_url
    checksum = var.resource_info.winetricks.checksum
    dl(url, download_dir, "winetricks", checksum=checksum)


def download_java():
    """
    Runs the download process for Java.
    <!-- Called in step.workarounds.apply_workarounds if needed -->
    """

    logger.debug("Initiating Java download...")
    url = var.resource_info.java.download_url
    checksum = var.resource_info.java.checksum
    path_internal = var.resource_info.java.path_internal
    checksum_internal = var.resource_info.java.checksum_internal
    downloaded = dl(url, download_dir, checksum=checksum)
    extracted = extract(downloaded, extract_dir / downloaded.stem)
    file_whitelist = (
        var.resource_info.java.file_whitelist
        if var.resource_info.java.file_whitelist
        else None
    )

    if extracted and extracted.exists():
        if not compare_checksum(extracted / path_internal, checksum_internal):
            logger.error(
                "Downloaded Java archive checksum does not match expected. Removing download and aborting installation."
            )
            downloaded.unlink(missing_ok=True)
            extracted.rmdir()
            return

    match state.current_instance.launcher:
        case "steam":
            subpath = Path("pfx") / "drive_c"
        case "gog" | "epic" | _:
            subpath = Path("drive_c")

    install_dir = var.prefix / subpath / "java"
    if install_dir.exists():
        rmtree(install_dir)

    install(extracted, install_dir, file_whitelist)


def download_scriptextender():
    """
    Runs the download and installation process for the game's script extender.
    """
    logger.debug("Initiating script extender download...")
    game_info = var.game_info
    script_extenders = game_info.script_extenders if game_info is not None else None
    matches = {}
    choice = None

    if script_extenders:
        for i, entry in enumerate(script_extenders or []):
            match = (
                entry.runtime.get(var.launcher)
                if isinstance(entry.runtime, dict)
                else entry.runtime
            )
            if match:
                matches[i] = entry

    if matches:
        match_count = len(matches)
        if match_count < 1 or None:
            logger.error("No script extender entries available for this game.")
            return
        elif match_count == 1:
            logger.debug("Single script extender version found; selecting by default.")
            choice = matches[0]
        elif match_count > 1:
            logger.debug(
                "Multiple script extender versions found; prompting user for selection."
            )
            choice = lang.prompt_install_scriptextender_choice(matches)
            logger.debug(f"User selected script extender version index: {choice}")
            index = choice if (0 < choice <= match_count) else None
            choice = matches[index]
            logger.trace(f"Selected entry: {choice}")
    else:
        logger.warning("No matching script extender versions found for this launcher.")
        return

    src = [None, None, None]  # [download source, checksum, file whitelist]
    if choice is None:
        logger.error("No valid script extender version selected; aborting download.")
        return
    else:
        download_info = getattr(choice, "download", None)
        if getattr(download_info, "direct", None):
            logger.debug("Determined download source as direct URL.")
            direct = getattr(download_info, "direct", None)
            if getattr(download_info, "nexus", None):
                logger.warning(
                    f"Both direct download URL and Nexus IDs provided for script extender version {getattr(choice, 'version', None)}. Preferring direct URL."
                )
            if isinstance(direct, dict):
                src[0] = direct.get("url", None)
            else:
                src[0] = direct
            if getattr(direct, "checksum", None):
                src[1] = getattr(direct, "checksum", None)
            else:
                src[1] = getattr(download_info, "checksum", None)
        elif getattr(download_info, "nexus", None):
            logger.debug("Determined download source as Nexus Mods.")
            nexus_info = getattr(download_info, "nexus", None)
            mod_id = nexus_info.get("mod", None)
            file_id = nexus_info.get("file", None)
            src[0] = f"nxm(mod={mod_id}, file={file_id})"
            if getattr(nexus_info, "checksum", None):
                src[1] = getattr(nexus_info, "checksum", None)
            else:
                src[1] = getattr(download_info, "checksum", None)
        else:
            logger.error(
                f"No valid download source found for script extender version {getattr(choice, 'version', None)}."
            )
            return
        logger.debug(f"Download source determined: {src[0]}")
        src[2] = getattr(choice, "file_whitelist", None)

        if src[0].startswith("http"):
            logger.debug(
                f"Downloading script extender version {getattr(choice, 'version', None)} from URL: {src[0]}"
            )
            downloaded = dl(src[0], download_dir, checksum=src[1])
        elif src[0].startswith("nxm"):
            logger.debug(
                f"Downloading script extender version {getattr(choice, 'version', None)} from Nexus Mods: mod_id={mod_id}, file_id={file_id}"
            )
            downloaded = nexus_dl(
                var.game_info.nexus_slug,
                mod_id,
                file_id,
                download_dir,
                checksum=src[1],
            )

    extract(downloaded, extract_dir / "scriptextender" / downloaded.name)
    install(
        extract_dir / "scriptextender" / downloaded.name,
        Path(var.game_install_path),
        src[2],
    )


def download_plugin(plugin: str):
    """
    Downloads and installs the specified plugin from its manifest.

    Parameters
    ----------
    plugin : str
        The identifier of the plugin to download.
    """
    manifest = {}
    if plugin not in [entry for entry in var.plugin_info]:
        logger.error(f"Plugin {plugin} not found in plugin information.")
        return
    logger.debug(f"Checking for {plugin} manifest...")
    manifest[plugin] = var.plugin_info[plugin].manifest

    if not manifest[plugin]:
        logger.error(f"No manifest URL specified for plugin: {plugin}")
        return
    logger.trace(f"Plugin manifest URL for {plugin}: {manifest[plugin]}")

    file = Path(request(manifest[plugin])[0])
    with open(file, "r") as f:
        data = json.loads(f.read())
        logger.trace(f"Downloaded plugin manifest for {plugin}: {data}")

    if not data:
        logger.error(f"Failed to download or parse manifest for plugin: {plugin}")
        return

    latest = data.get("Versions", [])[-1]
    file_path = latest.get("PluginPath")
    if file_path:
        if isinstance(file_path, list):
            file_path = tuple(file_path)
        elif isinstance(file_path, str):
            file_path = (file_path,)
    file_path = var.FileWhitelist(paths=file_path) if file_path else None

    url = latest.get("DownloadUrl")

    destination = download_dir / "plugins" / plugin
    downloaded = dl(url, destination, url.split("/")[-1])
    extract_dest = extract_dir / "plugins" / plugin / downloaded.name

    destination = cache_dir / "plugins" / plugin
    extract(downloaded, extract_dest)
    install(extract_dest, var.input_params.directory / "plugins", file_path)
    logger.debug(f"Plugin {plugin} installed to plugins directory.")


def extract(target: Path, destination: Path) -> Path:
    """
    Extracts the specified archive to the given destination.

    Parameters
    ----------
    target : Path
        The archive file to extract.
    destination : Path
        The directory to extract the archive into.

    Returns
    -------
    Path
        The path to the extraction destination.
    """
    if not target.exists():
        logger.error(f"Target archive {target} does not exist; cannot extract.")
        return None
    if destination.exists():
        logger.debug(
            f"Extraction destination {destination} already exists; skipping extraction."
        )
        return destination
    logger.debug(f"Extracting {target} to {destination}...")
    unzip(str(target), outdir=destination)
    return destination


def install(
    source: Path, destination: Path, file_list: Optional[var.FileWhitelist] = None
) -> Path:
    """
    Copies files from source to destination.

    Parameters
    ----------
    source : Path
        The source path to copy files from.
    destination : Path
        The destination path to copy files to.
    file_list : FileWhitelist, optional
        A list of specific files or directories to copy from source to destination.

    Returns
    -------
    Path
        The path to the destination where files were copied.
    """

    if file_list and file_list.subdirectory:
        subdirectory = file_list.subdirectory
        source = source / subdirectory
        logger.debug(f"Adjusted source path with subdirectory: {source}")
        file_list = file_list.paths if file_list.paths else None

    if not source.exists():
        logger.error(f"Source path {source} does not exist; cannot install.")
        return None

    destination.mkdir(parents=True, exist_ok=True)

    if not file_list or file_list in (["*"], "*", ("*",), []):
        logger.debug(f"Installing all files from {source} to {destination}.")
        if source.is_dir():
            copytree(source, destination, dirs_exist_ok=True)
        elif source.is_file():
            copy(source, destination)

    else:
        file_list = (
            var.FileWhitelist(paths=file_list)
            if isinstance(file_list, tuple)
            else var.FileWhitelist(paths=tuple(file_list))
            if isinstance(file_list, list)
            else var.FileWhitelist(
                paths=tuple(
                    file_list,
                )
            )
            if isinstance(file_list, str)
            else file_list
            if isinstance(file_list, var.FileWhitelist)
            else None
        )
        logger.debug(
            f"Installing specified files from {source} to {destination}: {file_list.paths}"
        )
        for file in file_list.paths:
            file = source / file
            dest = destination / file.name
            if file.is_dir():
                copytree(file, dest, dirs_exist_ok=True)
            else:
                if not file.parent.exists():
                    file.parent.mkdir(parents=True, exist_ok=True)
                copy(file, dest)
            logger.trace(f"Installed {file} to {dest}.")

    return destination


def download():
    """
    Runs the download process for all required external resources.
    """
    cache_dir.mkdir(parents=True, exist_ok=True)
    params = var.input_params
    game_info = var.game_info
    script_extenders = game_info.script_extenders if game_info is not None else None

    download_mod_organizer()
    if params.plugins:
        for plugin in params.plugins:
            download_plugin(plugin)
    download_winetricks()
    if params.script_extender:
        for entry in script_extenders or []:
            match = False
            if entry.runtime:
                runtime = (
                    entry.runtime.get(var.launcher)
                    if isinstance(entry.runtime, dict)
                    else entry.runtime
                )
                if runtime:
                    match = True
                    break
        if match:
            download_scriptextender()
    symlink_instance()
