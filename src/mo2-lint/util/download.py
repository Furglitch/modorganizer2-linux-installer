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
    filename = filename or url.split("/")[-1]
    export = dest / filename

    logger.debug(f"Attempting to download {filename} from {url}.")
    if export.exists():
        logger.trace(
            f"{filename} already exists at destination: {export}; skipping download."
        )
        return export

    for i in range(attempts):
        try:
            dl(url, export)
            if export.exists() and checksum:
                if compare_checksum(export, checksum):
                    logger.trace(
                        f"Successfully downloaded and verified {filename} from {url} on attempt {i + 1}."
                    )
                    return export
                else:
                    logger.trace(
                        f"Checksum mismatch for {filename} downloaded from {url} on attempt {i + 1}. Retrying."
                    )
                    export.unlink(missing_ok=True)
            elif export.exists():
                logger.trace(
                    f"Successfully downloaded {filename} from {url} on attempt {i + 1}."
                )
                return export
        except Exception as e:
            logger.exception(
                f"Failed to download {filename} from {url} on attempt {i + 1}. {e}"
            )
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

    dest.mkdir(parents=True, exist_ok=True)
    logger.debug(
        f"Attempting to download file_id {file_id} from mod_id {mod_id} for game {game} from Nexus Mods."
    )
    try:
        filename = nexus_dl(game, str(mod_id), str(file_id), dest, filename or None)
        export = dest / filename
        if export.exists() and checksum:
            if compare_checksum(export, checksum):
                logger.trace(
                    f"Successfully downloaded and verified file_id {file_id} from mod_id {mod_id} for game {game} from Nexus Mods."
                )
                return export
            else:
                logger.trace(
                    f"Checksum mismatch for file_id {file_id} from mod_id {mod_id} for game {game} from Nexus Mods. Retrying."
                )
                export.unlink(missing_ok=True)
        elif export.exists():
            logger.trace(
                f"Successfully downloaded file_id {file_id} from mod_id {mod_id} for game {game} from Nexus Mods."
            )
            return export
    except Exception as e:
        logger.exception(
            f"Failed to download file_id {file_id} from mod_id {mod_id} for game {game} from Nexus Mods. {e}"
        )
    return None
