#!/usr/bin/env python3

from loguru import logger
from pathlib import Path
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

    logger.trace(f"Calculating checksum for file: {target}")
    hash = hashlib.sha256()
    with open(target, "rb") as file:
        for byte_block in iter(lambda: file.read(4096), b""):
            hash.update(byte_block)
        digest = hash.hexdigest()
    logger.trace(f"Calculated checksum for {target}: {digest}")
    return digest


def compare_checksum(target_a: str | Path, target_b: str | Path) -> bool:
    """
    Compares the checksum of the target file against the source.

    Parameters
    ----------
    target_a : str | Path
        The first checksum as a string, or a Path to a file to calculate the checksum from.
    target_b : str | Path
        The second checksum as a string, or a Path to a file to calculate the checksum from.

    Returns
    -------
    bool
        True if the checksums match, False otherwise.
    """

    checksum_a = target_a if isinstance(target_a, str) else get_checksum(target_a)
    checksum_b = target_b if isinstance(target_b, str) else get_checksum(target_b)
    check_pass = checksum_a == checksum_b
    if check_pass:
        logger.trace(f"Checksum match: {checksum_a} == {checksum_b}")
    else:
        logger.trace(f"Checksum mismatch: {checksum_a} != {checksum_b}")

    return check_pass
