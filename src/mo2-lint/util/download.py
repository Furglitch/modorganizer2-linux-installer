#!/usr/bin/env python3

from loguru import logger
from pathlib import Path
from typing import Optional
from urllib.request import urlretrieve as dl
from util.checksum import compare_checksum
from util.nexus.download_mod import nexus_download as nexus_dl


def download(
    url: str, dest: Path, filename: Optional[str] = None, checksum: Optional[str] = None
) -> Path:
    """
    Downloads a file from the specified URL to the destination directory.

    Parameters
    ----------
    url : str
        The URL of the file to download.
    dest : Path
        The destination directory to save the file.
    filename : str, optional
        The name to save the file as. If None, uses the name from the URL.
    checksum : str, optional
        The expected checksum of the file for verification. If None, no verification is performed.
    Returns
    -------
    Path
        The path to the downloaded file.
    """

    attempts = 3
    dest.mkdir(parents=True, exist_ok=True)
    export = dest / (filename or url.split("/")[-1])

    if export.exists():
        logger.debug(f"File already exists at {export}, skipping download.")
        return export

    for i in range(attempts):
        logger.debug(f"Attempting to download {url} (Attempt {i + 1}/{attempts})")

        try:
            dl(url, export)
            if export.exists() and checksum:
                if compare_checksum(export, checksum):
                    logger.debug(f"Successfully downloaded and verified {export}")
                    return export
                else:
                    logger.warning(
                        f"Checksum verification failed for {export}. Retrying..."
                    )
                    export.unlink(missing_ok=True)
            elif export.exists():
                logger.debug(f"Successfully downloaded {export}")
                return export
        except Exception as e:
            logger.exception(
                f"Error downloading {url} on attempt {i + 1}/{attempts}: {e}",
                backtrace=True,
                diagnose=True,
            )
    logger.error(f"Failed to download {url} after {attempts} attempts.")
    return None


def download_nexus(
    game: str,
    mod_id: int,
    file_id: int,
    dest: Path,
    filename: Optional[str] = None,
    checksum: Optional[str] = None,
) -> Path:
    """
    Downloads a file from Nexus Mods.

    Parameters
    ----------
    game : str
        The game identifier on Nexus Mods.
    mod_id : int
        The ID of the mod.
    file_id : int
        The ID of the file to download.
    dest : Path
        The destination directory to save the file.
    filename : str, optional
        The name to save the file as. If None, uses the name from the URL.
    checksum : str, optional
        The expected checksum of the file for verification. If None, no verification is performed.

    Returns
    -------
    Path
        The path to the downloaded file.
    """

    attempts = 3
    dest.mkdir(parents=True, exist_ok=True)
    for i in range(attempts):
        logger.debug(
            f"Attempting to download Nexus Mods file {file_id} for mod {mod_id} (Attempt {i + 1}/{attempts})"
        )
        try:
            filename = nexus_dl(game, str(mod_id), str(file_id), dest, filename or None)
            export = dest / filename
            if export.exists() and checksum:
                if compare_checksum(export, checksum):
                    logger.debug(f"Successfully downloaded and verified {export}")
                    return export
                else:
                    logger.warning(
                        f"Checksum verification failed for {export}. Retrying..."
                    )
                    export.unlink(missing_ok=True)
            elif export.exists():
                logger.debug(f"Successfully downloaded {export}")
                return export
        except Exception as e:
            logger.exception(
                f"Error downloading Nexus Mods file {mod_id}:{file_id} on attempt {i + 1}/{attempts}: {e}",
                backtrace=True,
                diagnose=True,
            )
            continue
    logger.error(
        f"Failed to download Nexus Mods file {mod_id}:{file_id} after {attempts} attempts."
    )
    return None
