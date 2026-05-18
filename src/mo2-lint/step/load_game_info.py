#!/usr/bin/env python3

from loguru import logger
from pathlib import Path
from typing import Optional
from util import lang, variables as var, state_file as state
from util.heroic.find_library import get_data as get_heroic_data
from util.steam.find_library import get_libraries as get_steam_libraries


def get_launcher(launcher: Optional[str] = None) -> str:
    """
    Determines the launcher being used based on detected libraries.

    Parameters
    ----------
    launcher : str, optional
        If provided, skip auto-detection and use this launcher directly.
        Must be one of "steam", "gog", or "epic".

    Returns
    -------
    str
        The launcher type ("steam", "gog", "epic"), or None if not found.
    """

    if launcher:
        launcher = launcher.lower()
        if launcher not in ("steam", "gog", "epic"):
            logger.error(
                f"Invalid launcher specified: {launcher}. Must be one of: steam, gog, epic."
            )
            return None
        logger.debug(f"Using specified launcher: {launcher}")
        var.launcher = launcher
        return var.launcher

    logger.debug("Detecting game launchers.")
    steam_libraries = get_steam_libraries()
    heroic_data = get_heroic_data()

    steam_has_game = False
    heroic_has_game = False
    steam_install_path = None
    heroic_install_path = None

    if steam_libraries:
        for lib in steam_libraries:
            subdir = (
                var.game_info.subdirectory.get("steam")
                if isinstance(var.game_info.subdirectory, dict)
                else var.game_info.subdirectory
            )
            if subdir is not None:
                steam_install_path = Path(lib) / "steamapps" / "common" / subdir
                if steam_install_path.exists():
                    steam_has_game = True
                    break
    if heroic_data and isinstance(heroic_data[2], Path):
        heroic_has_game = True
        heroic_install_path = heroic_data[2]
    elif heroic_data and isinstance(heroic_data[2], dict):
        heroic_has_game = True
        gog_install_path = heroic_data[2].get("gog")
        epic_install_path = heroic_data[2].get("epic")

    var.launcher = None
    if steam_has_game and heroic_has_game:
        logger.trace(
            "Multiple game installations detected. Prompting user for launcher choice."
        )

        gog_install_path = None
        epic_install_path = None
        if heroic_install_path:
            if heroic_data[0] == "gog":
                gog_install_path = heroic_install_path
            elif heroic_data[0] == "epic":
                epic_install_path = heroic_install_path

        choice = (
            lang.prompt_launcher_choice(
                steam_install_path if steam_install_path else None,
                gog_install_path if gog_install_path else None,
                epic_install_path if epic_install_path else None,
            )
            .split(":")[0]
            .strip()
            .lower()
        )
        if choice == "steam":
            var.launcher = "steam"
        elif choice == "gog":
            var.launcher = "gog"
        elif choice == "epic":
            var.launcher = "epic"
        else:
            logger.error(f"Invalid launcher choice: {choice}")
            return None
    elif steam_has_game:
        var.launcher = "steam"
    elif heroic_has_game and heroic_data[0] == "gog":
        var.launcher = "gog"
    elif heroic_has_game and heroic_data[0] == "epic":
        var.launcher = "epic"
    else:
        logger.error(
            "No supported game launchers detected. Please ensure you have the game installed through Steam, GOG, or Epic Games."
        )
        return None
    logger.trace(f"Detected launcher: {var.launcher}")
    return var.launcher


def get_library() -> Path:
    """
    Determines the installation path of the selected game based on the detected launcher.

    Returns
    -------
    Path
        Path representing the game's installation directory, or None if not found.
    """

    logger.debug(f"Determining game installation path for launcher: {var.launcher}")
    chosen_game = var.game_info
    subdir = (
        chosen_game.subdirectory.get(var.launcher)
        if isinstance(chosen_game.subdirectory, dict)
        else chosen_game.subdirectory
    )
    executable = (
        chosen_game.executable.get(var.launcher)
        if isinstance(chosen_game.executable, dict)
        else chosen_game.executable
    )

    library = None
    if var.launcher == "steam":
        libraries = get_steam_libraries()
        if len(libraries) == 0:
            logger.error(
                "No Steam libraries found. Cannot determine game installation path."
            )
            return None
        else:
            for lib in libraries:
                candidate = lib / "steamapps" / "common" / subdir
                if candidate.exists():
                    library = candidate
                    break
    elif var.launcher == "gog" or var.launcher == "epic":
        # Use cached heroic_config, or fetch it if not yet populated
        if not var.heroic_config or len(var.heroic_config) < 3:
            get_heroic_data()
        if var.heroic_config and len(var.heroic_config) >= 3:
            heroic_launcher, heroic_game_id, heroic_install_path, heroic_wine_prefix = (
                var.heroic_config
            )
            if isinstance(heroic_install_path, dict):
                library = heroic_install_path.get(var.launcher)
            else:
                library = heroic_install_path
        else:
            logger.error("Heroic configuration not available.")
            return None
        if not library:
            logger.error(f"Install path not found for {var.launcher}.")
            return None
    logger.trace(f"Determined {var.launcher} installation path: {library}")

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
        logger.trace(f"Determined game installation path: {library}")
        var.game_install_path = library
        return library
    else:
        logger.error("Failed to determine game installation path.")
        return None
