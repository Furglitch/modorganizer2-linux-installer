from loguru import logger
import os
import re
from pathlib import Path

steam_directories = [
    "${HOME}/.steam/root",
    "${HOME}/.var/app/com.valvesoftware.Steam/.local/share/Steam",
]
libraries = []


def get_libraries():
    """Retrieves Steam library paths from libraryfolders.vdf file"""
    for dir in steam_directories:
        dir = Path(os.path.expandvars(dir)).resolve()
        if dir.exists():
            logger.debug(f"Found Steam library at: {dir}")
            if Path(dir / "steamapps").exists():
                logger.debug(f"Found steamapps directory at: {dir / 'steamapps'}")
                library = dir
            else:
                library = dir / "steam"
            global libraries
            with open(
                library / "steamapps" / "libraryfolders.vdf", "r", encoding="utf-8"
            ) as file:
                libraries = re.findall(r'/[^"]+', file.read())
                logger.debug(f"Discovered Steam libraries: {libraries}")
    return libraries
