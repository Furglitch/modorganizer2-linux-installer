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
    url = var.resource_info.winetricks.download_url
    checksum = var.resource_info.winetricks.checksum
    dl(url, download_dir, "winetricks", checksum=checksum)


def download_java():
    url = var.resource_info.java.download_url
    checksum = var.resource_info.java.checksum
    downloaded = dl(url, download_dir, checksum=checksum)
    extract(downloaded, extract_dir / "java")


def download_scriptextender():
    entries = (
        var.game_info.get(var.input_params.game)
        .get("script_extender", {})
        .get(var.launcher)
    )

    index = 0
    if len(entries) > 1:
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
            index = int(sel) - 1 if (0 <= int(sel) - 1 < len(entries)) else None
        else:
            raise ValueError("No valid selection made for script extender version.")
    elif len(entries) == 1:
        index = 0
    else:
        logger.error("No script extender entries available for this game.")
        return None

    entry = entries[index]
    version = entry.get("version")
    runtime = entry.get("runtime") or None
    src = entry.get("download_url") or (
        f"nexus(mod={entry.get('mod_id')}, file={entry.get('file_id')})"
        if entry.get("mod_id") and entry.get("file_id")
        else None
    )
    checksum = entry.get("checksum") or None
    files = entry.get("files") or []

    if src.startswith("http"):
        downloaded = dl(src, download_dir, checksum=checksum)
    elif src.startswith("nexus"):
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
        for file in file_list:
            file = source / file
            dest = destination / file.name
            if dest.exists():
                dest.unlink(missing_ok=True)
            if file.is_dir():
                copytree(file, dest, dirs_exist_ok=True)
            else:
                copy(file, dest)
    elif file_list:
        copytree(source, destination, dirs_exist_ok=True)
    else:
        copy(source, destination)
