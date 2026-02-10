#!/usr/bin/env python3

from loguru import logger
from pathlib import Path
from util import variables as var
import os
import re

steam_directories = [
    "${HOME}/.steam/root",
    "${HOME}/.var/app/com.valvesoftware.Steam/.local/share/Steam",
]


def get_data() -> tuple[int, str, str]:
    """
    Gets Steam game data from the variable configuration.

    Returns
    -------
    tuple[int, str, str]
        A tuple containing the Steam ID, subdirectory, and executable.
    """

    chosen_game = var.game_info
    id = chosen_game.launcher_ids.steam
    subdir = chosen_game.subdirectory
    exe = chosen_game.executable

    logger.trace(
        f"Retrieved Steam game data: ID={id}, Subdirectory={subdir}, Executable={exe}"
    )
    return (id, subdir, exe)


def get_libraries() -> list[Path]:
    """
    Gets Steam game library directories from the Steam configuration files.

    Returns
    -------
    list[Path]
        A list of Path objects representing the Steam library directories.
    """

    libraries = []
    logger.debug(
        f"Searching {len(steam_directories)} potential Steam directories for library folders."
    )
    for dir in steam_directories:
        logger.trace(f"Checking Steam directory: {dir}")
        dir = Path(os.path.expandvars(dir)).resolve()
        if dir.exists():
            library = dir if Path(dir / "steamapps").exists() else dir / "steam"
            library_list = library / "steamapps" / "libraryfolders.vdf"
            if not library_list.exists():
                logger.trace(
                    f"libraryfolders.vdf not found in {library}, skipping this directory."
                )
                continue
            try:
                with open(library_list, "r", encoding="utf-8") as file:
                    libraries = re.findall(r"/[^\"]+", file.read())
                    for i in range(len(libraries)):
                        libraries[i] = Path(libraries[i])
                    logger.trace(f"Found Steam library folders: {libraries}")
            except Exception as e:
                logger.exception(f"Error reading libraryfolders.vdf in {library}: {e}")
        else:
            logger.trace(f"Steam directory does not exist: {dir}")
    logger.debug(f"Total Steam library directories found: {len(libraries)}")
    return libraries
