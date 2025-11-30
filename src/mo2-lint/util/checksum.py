#!/usr/bin/env python3

from pathlib import Path
from loguru import logger


def checksum_local(target: Path, expected: str) -> bool:
    logger.trace(f"Calculating checksum for: {target}")
    import hashlib

    hash = hashlib.sha256()
    with open(target, "rb") as file:
        for byte_block in iter(lambda: file.read(4096), b""):
            hash.update(byte_block)
        digest = hash.hexdigest()
    if digest == expected:
        check_pass = True
        logger.debug("Checksum matches expected value.")
    else:
        check_pass = False
        logger.warning("Checksum does not match expected value.")
    logger.trace(f"Calculated checksum: {digest}")
    logger.trace(f"Expected checksum: {expected}")
    return check_pass


def checksum_remote(url: str, expected: str) -> bool:
    logger.error("Remote checksum verification is not yet implemented.")  # TODO
    pass
