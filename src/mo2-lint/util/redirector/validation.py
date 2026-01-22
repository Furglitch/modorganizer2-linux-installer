#!/usr/bin/env python3

import util.variables as var
from pathlib import Path

internal_hash = None


def validate_redirector(game_install_path: Path = None) -> bool:
    from loguru import logger
    import hashlib

    global internal_hash

    if game_install_path is None:
        game_install_path = (
            Path(var.game_install_path)
            if not Path(var.game_install_path).is_file()
            else Path(var.game_install_path).parent
        )

    redirector_path = game_install_path / var.game_info.get("executable")
    if not redirector_path.exists():
        logger.error(f"Game executable not found at {redirector_path}")
        return False

    internal_redirector = var.internal_file("dist", "redirector.exe")

    hash = hashlib.sha256()
    with open(redirector_path, "rb") as file:
        for byte_block in iter(lambda: file.read(4096), b""):
            hash.update(byte_block)
        external_hash = hash.hexdigest()

    hash = hashlib.sha256()
    with open(internal_redirector, "rb") as file:
        for byte_block in iter(lambda: file.read(4096), b""):
            hash.update(byte_block)
        internal_hash = hash.hexdigest()

    print(f"External Hash: {external_hash}")
    print(f"Internal Hash: {internal_hash}")

    if external_hash == internal_hash:
        return True
    else:
        return False
