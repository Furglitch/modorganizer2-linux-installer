#!/usr/bin/env python3

from loguru import logger
from pathlib import Path
from patoolib import extract_archive as unzip
from shutil import copytree, copy2 as copy
from typing import Optional
from urllib.request import urlretrieve as request
from util.download import download as dl, download_nexus as nexus_dl
from util.state_file import symlink_instance
from util import variables as var
import json

cache_dir: Path = Path("~/.cache/mo2-lint").expanduser()
download_dir = cache_dir / "downloads"
extract_dir = download_dir / "extracted"


def download_mod_organizer():
    logger.debug("Initiating Mod Organizer 2 download...")
    url = var.resource_info.mod_organizer.download_url
    checksum = var.resource_info.mod_organizer.checksum
    downloaded = dl(url, download_dir, checksum=checksum)
    extract(downloaded, extract_dir / "mod_organizer")
    if downloaded.exists():
        destination = Path(var.input_params.directory).expanduser()
        destination.mkdir(parents=True, exist_ok=True)
        copytree(extract_dir / "mod_organizer", destination, dirs_exist_ok=True)
        logger.debug(f"Mod Organizer 2 installed to {destination}")


def download_winetricks():
    logger.debug("Initiating Winetricks download...")
    url = var.resource_info.winetricks.download_url
    checksum = var.resource_info.winetricks.checksum
    dl(url, download_dir, "winetricks", checksum=checksum)


def download_java():
    logger.debug("Initiating Java download...")
    url = var.resource_info.java.download_url
    checksum = var.resource_info.java.checksum
    downloaded = dl(url, download_dir, checksum=checksum)
    extract(downloaded, extract_dir / "java")


def download_scriptextender():
    logger.debug("Initiating script extender download...")
    entries = (
        var.game_info.get(var.input_params.game)
        .get("script_extender", {})
        .get(var.launcher)
    )

    index = 0
    if len(entries) > 1:
        logger.debug(
            "Multiple script extender versions found; prompting user for selection."
        )
        print("Multiple script extender versions are available for this game:")
        for i, entry in enumerate(entries):
            version = entry.get("version")
            runtime = entry.get("runtime") or None
            src = entry.get("download_url") or (
                f"nexus(mod={entry.get('mod_id')}, file={entry.get('file_id')})"
                if entry.get("mod_id") and entry.get("file_id")
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
    version = entry.get("version")
    runtime = entry.get("runtime") or None

    if entry.get("download_url"):
        if entry.get("mod_id") or entry.get("file_id"):
            logger.warning(
                f"Both direct download URL and Nexus mod/file IDs provided for script extender version {version}. Preferring direct URL."
            )
        else:
            logger.debug("Determined download source as direct URL.")
        src = entry.get("download_url")
    elif entry.get("mod_id") and entry.get("file_id"):
        logger.debug("Determined download source as Nexus Mods.")
        src = f"nexus(mod={entry.get('mod_id')}, file={entry.get('file_id')})"
    else:
        logger.error(
            f"No valid download source found for script extender version {version}."
        )
        return

    checksum = entry.get("checksum") or None
    files = entry.get("files") or []

    if src.startswith("http"):
        logger.debug(f"Downloading script extender version {version} from URL: {src}")
        downloaded = dl(src, download_dir, checksum=checksum)
    elif src.startswith("nexus"):
        logger.debug(
            f"Downloading script extender version {version} from Nexus Mods: mod_id={entry.get('mod_id')}, file_id={entry.get('file_id')}"
        )
        downloaded = nexus_dl(
            var.game_info.get(var.input_params.game).get("nexus_id"),
            entry.get("mod_id"),
            entry.get("file_id"),
            download_dir,
            checksum=checksum,
        )
    extract(downloaded, extract_dir / "scriptextender" / downloaded.name)
    install(
        extract_dir / "scriptextender" / downloaded.name,
        Path(var.input_params.directory),
        files,
    )


def download_plugin(plugin: str):
    manifest = {}
    for entry in var.plugin_info:
        if entry.get("Identifier") == plugin:
            manifest[plugin] = entry.get("Manifest")
            break

        file = Path(request(manifest.get(plugin))[0])
        with open(file, "r") as f:
            data = json(f.read())
            logger.trace(f"Downloaded plugin manifest for {plugin}: {data}")

        latest = data.get("Versions", [])[-1]
        file_path = latest.get("PluginPath")
        url = latest.get("DownloadUrl")

        destination = download_dir / "plugins" / plugin
        downloaded = dl(url, destination, url.split("/")[-1])

        destination = cache_dir / "plugins" / plugin
        extract(downloaded, destination / downloaded.name)

        install(destination, Path(var.input_params.directory) / "plugins", file_path)


def extract(target: Path, destination: Path):
    if destination.exists():
        logger.debug(
            f"Extraction destination {destination} already exists; skipping extraction."
        )
        return
    logger.debug(f"Extracting {target} to {destination}...")
    unzip(str(target), outdir=destination)


def download():
    cache_dir.mkdir(parents=True, exist_ok=True)
    if (
        var.input_params.script_extender is True
        and var.game_info.get(var.input_params.game).script_extenders.get(var.launcher)
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
    if not source.exists():
        logger.error(f"Source path {source} does not exist; cannot install.")
        return
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
