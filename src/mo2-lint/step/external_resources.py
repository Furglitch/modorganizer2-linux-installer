#!/usr/bin/env python3

from loguru import logger
from pathlib import Path
from patoolib import extract_archive as unzip
from shutil import copytree, copyfile as copy, rmtree
from typing import Optional
from urllib.request import urlopen, Request
from util import lang, variables as var, state_file as state
from util.checksum import compare_checksum
from util.download import download as dl, download_nexus as nexus_dl
from util.state_file import symlink_instance
import json
import stat
import ssl
import certifi

ssl_context = ssl.create_default_context(cafile=certifi.where())

cache_dir: Path = Path("~/.cache/mo2-lint").expanduser()
download_dir = cache_dir / "downloads"
extract_dir = download_dir / "extracted"


def download_mod_organizer():
    """
    Runs the download and installation process for Mod Organizer 2.
    """

    url = var.resource_info.mod_organizer.download_url
    checksum = var.resource_info.mod_organizer.checksum
    path_internal = var.resource_info.mod_organizer.path_internal
    checksum_internal = var.resource_info.mod_organizer.checksum_internal
    local_archive = var.input_params.mo2_archive
    destination = var.input_params.directory

    if local_archive:
        local_archive = Path(local_archive)
        logger.info(f"Installing Mod Organizer 2 from local archive: {local_archive}")
        if not compare_checksum(local_archive, var.input_params.mo2_checksum):
            logger.critical(
                f"Checksum mismatch for {local_archive}. Expected {var.input_params.mo2_checksum}."
            )
            raise SystemExit(1)
        downloaded = local_archive
        destination.mkdir(parents=True, exist_ok=True)
    else:
        logger.info("Starting download process for Mod Organizer 2")
        logger.trace(
            f"Download info: url={url}, checksum={checksum}, path_internal={path_internal}, checksum_internal={checksum_internal}"
        )
        downloaded = dl(url, download_dir, checksum=checksum)
        logger.debug(f"Downloaded Mod Organizer 2 to {downloaded}")

    extracted = extract(downloaded, extract_dir / downloaded.stem)
    if extracted and extracted.exists():
        logger.debug(f"Extracted Mod Organizer 2 to {extracted}")
        mo2_exec = destination / path_internal
        if (  # if ModOrganizer.exe exists in destination check if it's the same file
            not local_archive and destination.exists() and mo2_exec.exists()
        ):
            if not compare_checksum(mo2_exec, checksum_internal):
                if not lang.prompt_install_mo2_checksum_fail(str(mo2_exec)):
                    logger.info(
                        "User chose not to overwrite existing Mod Organizer 2 executable. Skipping installation."
                    )
                    return
        elif not destination.exists():
            destination.mkdir(parents=True, exist_ok=True)
    logger.debug(f"Installing Mod Organizer 2 to {destination}")
    install(extracted, destination, None)
    logger.success("Mod Organizer 2 download and installation complete.")


def download_winetricks():
    """
    Runs the download process for Winetricks.
    """
    logger.info("Starting download process for Winetricks")
    url = var.resource_info.winetricks.download_url
    checksum = var.resource_info.winetricks.checksum
    logger.trace(f"Download info: url={url}, checksum={checksum}")
    downloaded = dl(url, download_dir, "winetricks", checksum=checksum)
    if downloaded:
        downloaded.chmod(downloaded.stat().st_mode | stat.S_IEXEC)
    logger.success("Winetricks download complete.")


def download_java():
    """
    Runs the download process for Java.
    <!-- Called in step.workarounds.apply_workarounds if needed -->
    """
    logger.info("Starting download process for Java")
    url = var.resource_info.java.download_url
    checksum = var.resource_info.java.checksum
    path_internal = var.resource_info.java.path_internal
    checksum_internal = var.resource_info.java.checksum_internal
    logger.trace(
        f"Download info: url={url}, checksum={checksum}, path_internal={path_internal}, checksum_internal={checksum_internal}"
    )
    downloaded = dl(url, download_dir, checksum=checksum)
    logger.debug(f"Downloaded Java to {downloaded}")
    extracted = extract(downloaded, extract_dir / downloaded.stem)

    if extracted and extracted.exists():
        logger.debug(f"Extracted Java to {extracted}")
        if not compare_checksum(extracted / path_internal, checksum_internal):
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

    file_whitelist = (
        var.resource_info.java.file_whitelist
        if var.resource_info.java.file_whitelist
        else None
    )
    logger.debug(
        f"Installing Java to {install_dir} with file whitelist: {file_whitelist}"
    )
    install(extracted, install_dir, file_whitelist)
    logger.success("Java download and installation complete.")


def download_scriptextender():
    """
    Runs the download and installation process for the game's script extender.
    """

    logger.info("Starting download process for the game's script extender")
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
        keys = list(matches.keys())
        if match_count < 1 or None:
            return
        elif match_count == 1:
            choice = matches[keys[0]]
        elif match_count > 1:
            choice = lang.prompt_install_scriptextender_choice(matches)
            index = keys[choice] if 0 <= choice < match_count else None
            choice = matches[index] if index is not None else None
    else:
        return
    logger.debug(f"Chosen script extender entry: {choice}")

    src = [None, None, None]  # [download source, checksum, file whitelist]
    downloaded = None
    if choice is None:
        return
    else:
        download_info = getattr(choice, "download", None)
        if getattr(download_info, "direct", None):
            direct = getattr(download_info, "direct", None)
            if getattr(download_info, "nexus", None):
                logger.warning(
                    "Both direct download and Nexus download information found for the chosen script extender. Defaulting to direct download method."
                )
                pass
            if isinstance(direct, dict):
                src[0] = direct.get("url", None)
            else:
                src[0] = direct
            if getattr(direct, "checksum", None):
                src[1] = getattr(direct, "checksum", None)
            else:
                src[1] = getattr(download_info, "checksum", None)
            logger.debug(
                "Determined download method for script extender: direct download"
            )
        elif getattr(download_info, "nexus", None):
            nexus_info = getattr(download_info, "nexus", None)
            mod_id = nexus_info.get("mod", None)
            file_id = nexus_info.get("file", None)
            src[0] = f"nxm(mod={mod_id}, file={file_id})"
            logger.debug(
                "Determined download method for script extender: Nexus download"
            )
            if getattr(nexus_info, "checksum", None):
                src[1] = getattr(nexus_info, "checksum", None)
            else:
                src[1] = getattr(download_info, "checksum", None)
        else:
            return
        src[2] = getattr(choice, "file_whitelist", None)

        logger.info(
            "Starting download of script extender using method determined from manifest."
        )
        logger.trace(f"Download source: {src[0]}, checksum: {src[1]}")
        if src[0].startswith("http"):
            downloaded = dl(src[0], download_dir, checksum=src[1])
        elif src[0].startswith("nxm"):
            downloaded = nexus_dl(
                var.game_info.nexus_slug,
                mod_id,
                file_id,
                download_dir,
                checksum=src[1],
            )
    logger.debug(f"Downloaded script extender to {downloaded}")

    if not downloaded:
        logger.warning(
            "Could not automatically download Script Extender. Manual installation required."
        )
        logger.warning(
            "This may be due to an invalid API key or lack of Nexus Premium subscription."
        )
        return

    extract_path = extract_dir / "scriptextender" / downloaded.name
    extract(downloaded, extract_path)
    logger.debug(f"Extracted script extender to {extract_path}")
    installed_files = install_scriptextender(extract_path, src[2] if src[2] else None)

    if choice and getattr(choice, "version", None):
        state.current_instance.script_extender = choice.version
        state.current_instance.script_extender_files = installed_files
        logger.debug(f"Tracking installed script extender version: {choice.version}")
        logger.trace(f"Tracking {len(installed_files)} installed script extender files")

    logger.success("Script extender download and installation complete.")


def install_scriptextender(
    source: Path, whitelist: Optional[var.FileWhitelist] = None
) -> list[str]:
    """
    Installs the downloaded script extender to the game directory.

    Parameters
    ----------
    source : Path
        The path to the extracted script extender files.
    whitelist : FileWhitelist, optional
        A list of specific files or directories to copy from source to destination.

    Returns
    -------
    list[str]
        A list of relative paths for all files that were installed.
    """
    installed_files: list[str] = []

    if (
        var.input_params.plugins and "root-builder" in var.input_params.plugins
    ):  # If root_builder plugin is enabled, install Script Extender to mod root instead of game directory
        logger.info("Root builder plugin detected. Installing Script Extender via MO2")
        mod_root = var.input_params.directory / "mods" / "Script Extender"
        root_folder = mod_root / "root"
        data_folder = root_folder / "Data"

        logger.debug(f"Installing script extender root files to {root_folder}")
        _, installed_files = install(
            source,
            root_folder,
            whitelist,
        )

        if (
            data_folder.exists() and data_folder.is_dir()
        ):  # Move Data folder contents to mod root
            logger.debug(
                f"Moving Data folder contents from {data_folder} to {mod_root}"
            )
            for item in data_folder.iterdir():
                dest = mod_root / item.name
                if item.is_dir():
                    copytree(item, dest, dirs_exist_ok=True)
                    for file in dest.rglob("*"):
                        if file.is_file():
                            installed_files.append(str(file.relative_to(mod_root)))
                else:
                    copy(item, dest)
                    installed_files.append(str(dest.relative_to(mod_root)))
                logger.trace(f"Moved {item} to {dest}")
            rmtree(data_folder)

    else:  # Otherwise, install Script Extender to game directory
        destination = var.game_install_path
        logger.debug(
            f"Installing script extender to {destination} with whitelist {whitelist}"
        )
        _, installed_files = install(
            source,
            destination,
            whitelist,
        )

    return installed_files


def download_plugin(plugin: str):
    """
    Downloads and installs the specified plugin from its manifest or direct URL.

    Parameters
    ----------
    plugin : str
        The identifier of the plugin to download.
    """

    logger.info(f"Starting download process for plugin: {plugin}")
    if plugin not in var.plugin_info:
        return
    plugin_obj = var.plugin_info[plugin]
    url = None
    checksum = None
    file_whitelist = None

    if plugin_obj.direct:
        url = plugin_obj.direct
        checksum = plugin_obj.checksum
        file_whitelist = plugin_obj.file_whitelist
        logger.debug(f"Using direct download URL for plugin {plugin}: {url}")
    elif plugin_obj.manifest:
        logger.debug(f"Found manifest URL for plugin {plugin}: {plugin_obj.manifest}")
        req = Request(plugin_obj.manifest)
        with urlopen(req, context=ssl_context) as response:
            data = json.loads(response.read())
        if not data:
            return
        latest = data.get("Versions", [])[-1]
        file_path = latest.get("PluginPath")
        if file_path:
            file_path = (
                tuple(file_path) if isinstance(file_path, list) else (file_path,)
            )
        file_whitelist = var.FileWhitelist(paths=file_path) if file_path else None
        url = latest.get("DownloadUrl")
        logger.trace(
            f"Parsed manifest for plugin {plugin}: download URL: {url}, file whitelist: {file_whitelist}"
        )

    if not url:
        return

    destination = download_dir / "plugins" / plugin
    downloaded = dl(url, destination, url.split("/")[-1], checksum=checksum)
    logger.debug(f"Downloaded plugin {plugin} to {downloaded}")

    extract_dest = extract_dir / "plugins" / plugin / downloaded.name
    extract(downloaded, extract_dest)
    logger.debug(f"Extracted plugin {plugin} to {extract_dest}")

    install_dir = var.input_params.directory / "plugins"
    if plugin_obj.subdirectory:
        install_dir = install_dir / plugin_obj.subdirectory
    logger.trace(
        f"Installing plugin {plugin} to {install_dir} with whitelist {file_whitelist}"
    )
    install(extract_dest, install_dir, file_whitelist)
    logger.success(f"Plugin {plugin} download and installation complete.")


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
        logger.warning(f"Target archive {target} does not exist. Extraction skipped.")
        return None
    if destination.exists():
        logger.trace(
            f"Destination {destination} already exists. Skipping to avoid conflicts."
        )
        return destination
    logger.trace(f"Extracting archive {target} to destination {destination}")
    unzip(str(target), outdir=destination)
    logger.trace(f"Extraction of {target} complete.")
    return destination


def install(
    source: Path, destination: Path, file_list: Optional[var.FileWhitelist] = None
) -> tuple[Path, list[str]]:
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
    tuple[Path, list[str]]
        A tuple containing the path to the destination where files were copied,
        and a list of relative paths for all files that were installed.
    """

    installed_files: list[str] = []

    if file_list and file_list.subdirectory:
        subdirectory = file_list.subdirectory
        source = source / subdirectory
        file_list = file_list.paths if file_list.paths else None
    if not source.exists():
        logger.warning(f"Source path {source} does not exist. Installation skipped.")
        return None, []
    logger.trace(
        f"Installing from source {source} to destination {destination} with file list: {file_list}"
    )

    destination.mkdir(parents=True, exist_ok=True)
    logger.trace(f"Ensured destination directory exists: {destination}")

    if not file_list or file_list in (["*"], "*", ("*",), []):
        logger.trace(
            "No specific file list provided or file list indicates all files. Copying entire source directory."
        )
        if source.is_dir():
            # Collect all files from source before copying
            for item in source.rglob("*"):
                if item.is_file():
                    installed_files.append(str(item.relative_to(source)))
            copytree(source, destination, dirs_exist_ok=True)
        elif source.is_file():
            copy(source, destination)
            installed_files.append(source.name)

    else:
        if isinstance(file_list, var.FileWhitelist):
            pass
        elif isinstance(file_list, str):
            file_list = var.FileWhitelist(paths=(file_list,))
        elif isinstance(file_list, (list, tuple)):
            file_list = var.FileWhitelist(paths=tuple(file_list))
        logger.trace(
            f"Copying specific files from source to destination based on file list: {file_list}"
        )
        for file in file_list.paths:
            src = source / file
            dest = destination / Path(file).name
            if src.is_dir():
                # Collect all files from source directory before copying
                for item in src.rglob("*"):
                    if item.is_file():
                        installed_files.append(str(item.relative_to(source)))
                copytree(src, dest, dirs_exist_ok=True)
            else:
                if not src.parent.exists():
                    src.parent.mkdir(parents=True, exist_ok=True)
                copy(src, dest)
                installed_files.append(str(Path(file)))
            logger.trace(f"Copied {src} to {dest}")

    return destination, installed_files


def download():
    """
    Runs the download process for all required external resources.
    """
    cache_dir.mkdir(parents=True, exist_ok=True)
    params = var.input_params
    game_info = var.game_info
    script_extenders = game_info.script_extenders if game_info is not None else None

    logger.info("Starting download of external resources.")
    download_mod_organizer()
    game_plugins = tuple(getattr(game_info, "plugins", None) or ())
    all_plugins = list(params.plugins or ())
    for p in game_plugins:
        if p not in all_plugins:
            all_plugins.append(p)
    if all_plugins:
        for plugin in all_plugins:
            download_plugin(plugin)
    download_winetricks()
    if params.script_extender:
        match = False
        for entry in script_extenders or []:
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
    logger.success("All external resources downloaded and installed successfully.")
