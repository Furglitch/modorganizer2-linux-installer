#!/usr/bin/env python3

from pathlib import Path
from loguru import logger
import hashlib


def get_checksum(target: Path) -> str:
    """
    Calculates the SHA-256 checksum of the given file.

    Parameters
    ----------
    target : Path
        The file path to calculate the checksum for.
    Returns
    -------
    str
        The SHA-256 checksum as a string.
    """

    logger.trace(f"Getting checksum for: {target}")

    hash = hashlib.sha256()
    with open(target, "rb") as file:
        for byte_block in iter(lambda: file.read(4096), b""):
            hash.update(byte_block)
        digest = hash.hexdigest()
    logger.trace(f"Calculated checksum: {digest}")
    return digest


def compare_checksum(source: str | Path, target: Path) -> bool:
    """
    Compares the checksum of the target file against the source.

    Parameters
    ----------
    source : str | Path
        The source checksum as a string, or a Path to a file to calculate the checksum from.
    target : Path
        The target file to calculate the checksum from.

    Returns
    -------
    bool
        True if the checksums match, False otherwise.
    """

    logger.trace(f"Calculating checksum for: {target}")

    source_checksum = source if isinstance(source, str) else get_checksum(source)
    target_checksum = get_checksum(target)
    check_pass = source_checksum == target_checksum
    if check_pass:
        logger.trace("Checksum verification passed")
    else:
        logger.trace("Checksum verification failed")

    return check_pass
