#!/usr/bin/env python3

from loguru import logger
import os
import re
from pathlib import Path
from util.variables import input, game_info

steam_directories = [
    "${HOME}/.steam/root",
    "${HOME}/.var/app/com.valvesoftware.Steam/.local/share/Steam",
]


def get_data() -> tuple[int, str, str]:
    """
    Returns
    -------
    tuple[int, str, str]
        A tuple containing the Steam ID, subdirectory, and executable.
    """

    chosen_game = game_info.get(input.game)
    id = chosen_game.launcher_ids.steam
    subdir = chosen_game.subdirectory
    exe = chosen_game.executable

    return tuple(id, subdir, exe)


def get_libraries() -> list[Path]:
    """
    Returns a list of Steam library paths found on the system.

    Returns
    -------
    list[Path]
        A list of Path objects representing the Steam library directories.
    """

    libraries = []
    for dir in steam_directories:
        dir = Path(os.path.expandvars(dir)).resolve()
        if dir.exists():
            logger.debug(f"Found Steam library at: {dir}")
            library = dir if Path(dir / "steamapps").exists() else dir / "steam"
            library_list = library / "steamapps" / "libraryfolders.vdf"
            if not library_list.exists():
                continue
            with open(library_list, "r", encoding="utf-8") as file:
                libraries = re.findall(r'/[^"]+', file.read())
                for i in range(len(libraries)):
                    libraries[i] = Path(libraries[i])
                logger.debug(f"Discovered Steam libraries: {libraries}")
    return libraries
