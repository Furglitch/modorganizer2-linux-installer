#!/usr/bin/env python3

from loguru import logger
from pathlib import Path
from patoolib import extract_archive as unzip
from shutil import copytree, copy2 as copy
from typing import Optional
from urllib.request import urlretrieve as request
from util import variables as var, state_file as state
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
    checksum = var.resource_info.mod_organizer.internal_checksum
    downloaded = dl(url, download_dir, checksum=checksum)
    extract(downloaded, extract_dir / "mod_organizer")
    pinned = (
        state.current_instance.pin
        if state.current_instance and hasattr(state.current_instance, "pin")
        else False
    )
    if downloaded.exists():
        destination = Path(var.input_params.directory).expanduser()
        mo2_exec = destination / "ModOrganizer.exe"
        if (  # if ModOrganizer.exe exists in destination check if it's the same file
            destination.exists() and mo2_exec.exists()
        ) and not pinned:
            if not compare_checksum(mo2_exec, checksum):
                print(
                    f"Mod Organizer 2 already exists at {mo2_exec}, but checksums do not match. There may have been an update."
                )
                response = input("Continue and overwrite? [Y/n]: ")
                if response.lower() not in ("y", "yes", ""):
                    logger.info(
                        "User opted to not overwrite existing Mod Organizer 2 installation."
                    )
                    return
        elif pinned:
            logger.info(
                f"Mod Organizer 2 installation at {mo2_exec} is pinned; skipping update."
            )
            return
        elif not destination.exists():
            destination.mkdir(parents=True, exist_ok=True)
        install(extract_dir / "mod_organizer", destination, None)
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
    checksum = var.resource_info.java.internal_checksum
    downloaded = dl(url, download_dir, checksum=checksum)
    extract(downloaded, extract_dir / "java")


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
            match = getattr(entry, "runtime", None).get(var.launcher)
            if match:
                matches[i] = entry

    if matches:
        match_count = len(matches)
        if match_count <= 0 or None:
            logger.error("No script extender entries available for this game.")
            return
        elif match_count == 1:
            logger.debug("Single script extender version found; selecting by default.")
            index = 0
        elif match_count > 1:
            logger.debug(
                "Multiple script extender versions found; prompting user for selection."
            )
            print("Multiple script extender versions are available for this game:")
            for entry in matches.values():
                i = list(matches.values()).index(entry)
                version = getattr(entry, "version", None)
                runtime = getattr(entry, "runtime", None)
                runtime = runtime.get(var.launcher) if runtime else None
                _runtime = None
                if isinstance(runtime, dict):
                    for key, value in runtime.items():
                        if isinstance(value, list):
                            _runtime[key] = ", ".join(value)
                        else:
                            _runtime[key] = [value]
                else:
                    _runtime = runtime
                print(f"  - {i + 1}: {version} for {_runtime}")
            choice = input(f"Choose version [1-{match_count}] (default: 1): ").strip()
            if not choice.isdigit():
                logger.critical(
                    "No valid selection made for script extender version. Aborting download."
                )
                return
            else:
                choice = int(choice) - 1
                logger.debug(f"User selected script extender version index: {choice}")
                index = choice if (0 <= choice < match_count) else None
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
    url = latest.get("DownloadUrl")

    destination = download_dir / "plugins" / plugin
    downloaded = dl(url, destination, url.split("/")[-1])
    extract_dest = extract_dir / "plugins" / plugin / downloaded.name

    destination = cache_dir / "plugins" / plugin
    extract(downloaded, extract_dest)
    install(extract_dest, Path(var.input_params.directory) / "plugins", file_path)
    logger.debug(f"Plugin {plugin} installed to plugins directory.")


def extract(target: Path, destination: Path):
    """
    Extracts the specified archive to the given destination.

    Parameters
    ----------
    target : Path
        The archive file to extract.
    destination : Path
        The directory to extract the archive into.
    """
    if destination.exists():
        logger.debug(
            f"Extraction destination {destination} already exists; skipping extraction."
        )
        return
    logger.debug(f"Extracting {target} to {destination}...")
    unzip(str(target), outdir=destination)


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
            runtime = getattr(entry, "runtime", None)
            if runtime and runtime.get(var.launcher):
                match = runtime.get(var.launcher)
        if match:
            download_scriptextender()
    symlink_instance()


def install(source: Path, destination: Path, file_list: Optional[list[str] | str]):
    """
    Copies files from source to destination.

    Parameters
    ----------
    source : Path
        The source path to copy files from.
    destination : Path
        The destination path to copy files to.
    file_list : list[str] | str, optional
        A list of specific files to copy. If None, empty, or wildcard, all files are copied.
    """
    if not source.exists():
        logger.error(f"Source path {source} does not exist; cannot install.")
        return
    destination.mkdir(parents=True, exist_ok=True)
    if not file_list or file_list in (["*"], "*", []):
        logger.debug(f"Installing all files from {source} to {destination}.")
        if source.is_dir():
            copytree(source, destination, dirs_exist_ok=True)
        elif source.is_file():
            copy(source, destination)
    else:
        logger.debug(
            f"Installing specified files from {source} to {destination}: {file_list}"
        )
        for file in file_list:
            file = source / file
            dest = destination / file.name
            if file.is_dir():
                copytree(file, dest, dirs_exist_ok=True)
            else:
                copy(file, dest)
            logger.trace(f"Installed {file} to {dest}.")
