#!/usr/bin/env python3

from loguru import logger
from pathlib import Path
from patoolib import extract_archive as unzip
from shutil import copytree, copy2 as copy
from typing import Optional
from urllib.request import urlretrieve as request
from util import variables as var
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
    if downloaded.exists():
        destination = Path(var.input_params.directory).expanduser()
        mo2_exec = destination / "ModOrganizer.exe"
        if (
            destination.exists() and mo2_exec.exists()
        ):  # if ModOrganizer.exe exists in destination
            # check if it's the same file
            if not compare_checksum(mo2_exec, checksum):
                print(
                    f"Mod Organizer 2 already exists at {mo2_exec}, but checksums do not match. There may have been an update."
                )
                response = input("Continue and overwrite? [Y/n]: ")
                if not response.lower() == ("y" or "yes" or ""):
                    logger.info(
                        "User opted to not overwrite existing Mod Organizer 2 installation."
                    )
                    return
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
    gi = var.game_info.get(var.input_params.game) or None
    entries = getattr(gi.script_extenders, var.launcher) if gi is not None else []

    index = 0
    if len(entries) > 1:
        logger.debug(
            "Multiple script extender versions found; prompting user for selection."
        )
        print("Multiple script extender versions are available for this game:")
        for i, entry in enumerate(entries):
            version = getattr(entry, "version", None)
            runtime = getattr(entry, "runtime", None)
            src = getattr(entry, "download_url", None) or (
                f"nexus(mod={getattr(entry, 'mod_id', None)}, file={getattr(entry, 'file_id', None)})"
                if getattr(entry, "mod_id", None) and getattr(entry, "file_id", None)
                else None
            )
            if runtime:
                msg = f"{version} for {runtime} - {src}"
            else:
                msg = f"{version} - {src}"
            print(f"{i + 1}: {msg}")
        sel = input(
            f"Choose version [1-{len(entries)}] (default {len(entries)}): "
        ).strip()
        if sel.isdigit():
            logger.debug(f"User selected script extender version index: {sel}")
            index = int(sel) - 1 if (0 <= int(sel) - 1 < len(entries)) else None
            logger.trace(f"Selected entry: {entries[index]}")
        else:
            logger.error("No valid selection made for script extender version.")
            raise ValueError("No valid selection made for script extender version.")
    elif len(entries) == 1:
        index = 0
        logger.debug("Single script extender version found; selecting by default.")
    else:
        logger.error("No script extender entries available for this game.")
        return None

    entry = entries[index]
    version = getattr(entry, "version", None)
    runtime = getattr(entry, "runtime", None)

    if getattr(entry, "download_url", None):
        if getattr(entry, "mod_id", None) or getattr(entry, "file_id", None):
            logger.warning(
                f"Both direct download URL and Nexus mod/file IDs provided for script extender version {version}. Preferring direct URL."
            )
        else:
            logger.debug("Determined download source as direct URL.")
        src = getattr(entry, "download_url", None)
    elif getattr(entry, "mod_id", None) and getattr(entry, "file_id", None):
        logger.debug("Determined download source as Nexus Mods.")
        src = f"nexus(mod={getattr(entry, 'mod_id', None)}, file={getattr(entry, 'file_id', None)})"
    else:
        logger.error(
            f"No valid download source found for script extender version {version}."
        )
        return

    checksum = getattr(entry, "checksum", None)
    files = getattr(entry, "files", []) or []

    if src.startswith("http"):
        logger.debug(f"Downloading script extender version {version} from URL: {src}")
        downloaded = dl(src, download_dir, checksum=checksum)
    elif src.startswith("nexus"):
        logger.debug(
            f"Downloading script extender version {version} from Nexus Mods: mod_id={getattr(entry, 'mod_id', None)}, file_id={getattr(entry, 'file_id', None)}"
        )
        downloaded = nexus_dl(
            var.game_info.get(var.input_params.game).get("nexus_id"),
            getattr(entry, "mod_id", None),
            getattr(entry, "file_id", None),
            download_dir,
            checksum=checksum,
        )
    extract(downloaded, extract_dir / "scriptextender" / downloaded.name)
    install(
        extract_dir / "scriptextender" / downloaded.name,
        Path(var.game_install_path),
        files,
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
    gi = var.game_info.get(var.input_params.game)
    if (
        var.input_params.script_extender is True
        and (
            getattr(gi.script_extenders, var.launcher, None) if gi is not None else None
        )
        is not None
    ):
        download_scriptextender()
    download_mod_organizer()
    download_winetricks()
    download_java()  # ! Specify only for required games
    if var.input_params.plugins:
        for plugin in var.input_params.plugins:
            download_plugin(plugin)
    symlink_instance()


def install(source: Path, destination: Path, file_list: Optional[list[str]]):
    """
    Copies files from source to destination.

    Parameters
    ----------
    source : Path
        The source path to copy files from.
    destination : Path
        The destination path to copy files to.
    file_list : list[str], optional
        A list of specific files to copy. If None, empty, or wildcard, all files are copied.
    """
    if not source.exists():
        logger.error(f"Source path {source} does not exist; cannot install.")
        return
    destination.mkdir(parents=True, exist_ok=True)
    if source.is_file():
        if file_list and file_list != (["*"] or "*" or [] or None):
            logger.debug(
                f"Installing specified files from {source} to {destination}: {file_list}"
            )
            for file in file_list:
                file = source / file
                dest = destination / file.name
                if dest.exists():
                    dest.unlink(missing_ok=True)
                if file.is_dir():
                    copytree(file, dest, dirs_exist_ok=True)
                else:
                    copy(file, dest)
        else:
            logger.debug(f"Installing all files from {source} to {destination}.")
            if source.is_dir():
                copytree(source, destination, dirs_exist_ok=True)
            elif source.is_file():
                copy(source, destination)
    elif source.is_dir():
        logger.debug(f"Installing all files from {source} to {destination}.")
        copytree(source, destination, dirs_exist_ok=True)
