#!/usr/bin/env python3

from util.variables import input, game_info, launcher
from util.steam.find_library import get_libraries as get_steam_libraries
from util.heroic.find_library import get_data as get_heroic_data, gog_data, epic_data
from util.state_file import current_instance as instance
from loguru import logger
from pathlib import Path


def get_library() -> Path | None:
    """
    Returns
    -------
    Path
        Path representing the game's installation directory, or None if not found.
    """

    chosen_game = game_info.get(input.game)
    subdirectory = chosen_game.subdirectory
    executable = chosen_game.executable

    if launcher == "steam":
        libraries = get_steam_libraries()
        if len(libraries) == 0:
            logger.error("No Steam libraries found.")
            return None
        else:
            for library in libraries:
                library = library / "steamapps" / "common" / subdirectory
                if library.exists():
                    break

    if launcher == ("gog" or "epic"):
        get_heroic_data()
        library = (
            gog_data["install_path"]
            if launcher == "gog"
            else epic_data["install_path"]
            if launcher == "epic"
            else None
        )

    if library and library.exists():
        instance.launcher = launcher
        instance.game_path = str(library)
        instance.game_executable = executable
        instance.launcher_ids = {
            "steam_id": chosen_game.launcher_ids.steam,
            "gog_id": chosen_game.launcher_ids.gog,
            "epic_id": chosen_game.launcher_ids.epic,
        }
        logger.debug(f"Determined game installation path: {library}")
        return library
    else:
        logger.error("Could not determine game installation path.")
        return None
