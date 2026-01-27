#!/usr/bin/env python3

from util import variables as var, state_file as state
from util.steam.find_library import get_libraries as get_steam_libraries
from util.heroic.find_library import get_data as get_heroic_data, gog_data, epic_data
from loguru import logger
from pathlib import Path


def get_launcher() -> str | None:
    """
    Determines the launcher being used based on detected libraries.

    Returns
    -------
    str
        The launcher type ("steam", "gog", "epic"), or None if not found.
    """

    logger.debug("Detecting available launchers")
    steam_libraries = get_steam_libraries()
    heroic_data = get_heroic_data()
    var.launcher = None
    if steam_libraries and heroic_data[0]:
        logger.error(
            "Both Steam and Heroic launchers detected. Functionality not yet implemented."
        )  # TODO
    elif steam_libraries:
        var.launcher = "steam"
    elif heroic_data[0] == "gog":
        var.launcher = "gog"
    elif heroic_data[0] == "epic":
        var.launcher = "epic"
    else:
        logger.error("No supported launchers detected.")
    logger.debug(f"Determined launcher: {var.launcher}")
    return var.launcher


def get_library() -> Path | None:
    """
    Determines the installation path of the selected game based on the detected launcher.

    Returns
    -------
    Path
        Path representing the game's installation directory, or None if not found.
    """

    logger.debug(f"Looking up library for game={var.input_params.game}")
    chosen_game = var.game_info.get(var.input_params.game)
    subdirectory = chosen_game.subdirectory
    executable = chosen_game.executable

    if var.launcher == "steam":
        libraries = get_steam_libraries()
        if len(libraries) == 0:
            logger.error("No Steam libraries found.")
            return None
        else:
            for library in libraries:
                library = library / "steamapps" / "common" / subdirectory
                if library.exists():
                    break

    if var.launcher == ("gog" or "epic"):
        get_heroic_data()
        library = (
            gog_data["install_path"]
            if var.launcher == "gog"
            else epic_data["install_path"]
            if var.launcher == "epic"
            else None
        )

    if state.current_instance:
        state.current_instance.launcher = var.launcher
        state.current_instance.game_path = library
        state.current_instance.game_executable = executable
        state.current_instance.launcher_ids = var.LauncherIDs.from_dict(
            {
                "steam": chosen_game.launcher_ids.steam,
                "gog": chosen_game.launcher_ids.gog,
                "epic": chosen_game.launcher_ids.epic,
            }
        )
    if library and library.exists():
        logger.debug(f"Determined game installation path: {library}")
        var.game_install_path = library
        return library
    else:
        logger.error("Could not determine game installation path.")
        return None
