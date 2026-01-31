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

    chosen_game = var.game_info.get(var.input_params.game)
    id = chosen_game.launcher_ids.steam
    subdir = chosen_game.subdirectory
    exe = chosen_game.executable

    logger.trace(
        f"Steam library data for {var.input_params.game}: id={id}, subdir={subdir}, exe={exe}"
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
    logger.debug(f"Scanning {len(steam_directories)} candidate Steam directories")
    for dir in steam_directories:
        dir = Path(os.path.expandvars(dir)).resolve()
        logger.trace(f"Checking candidate Steam dir: {dir}")
        if dir.exists():
            logger.debug(f"Found Steam library at: {dir}")
            library = dir if Path(dir / "steamapps").exists() else dir / "steam"
            library_list = library / "steamapps" / "libraryfolders.vdf"
            if not library_list.exists():
                logger.warning(f"libraryfolders.vdf not found at {library_list}")
                continue
            try:
                with open(library_list, "r", encoding="utf-8") as file:
                    libraries = re.findall(r"/[^\"]+", file.read())
                    for i in range(len(libraries)):
                        libraries[i] = Path(libraries[i])
                    logger.debug(f"Discovered Steam libraries: {libraries}")
            except Exception:
                logger.exception(
                    f"Failed to parse {library_list}", backtrace=True, diagnose=True
                )
    logger.debug(f"Returning {len(libraries)} Steam libraries")
    return libraries
