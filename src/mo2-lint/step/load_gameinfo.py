#!/usr/bin/env python3

from loguru import logger
import os
import util.state.state_file as state


def get_steam_data():
    from util.variables import game_info

    id = game_info.get("steam_id")
    subdir = game_info.get("steam_subdirectory")
    exe = game_info.get("executable")
    id_valid = isinstance(id, int) and id > 0
    subdir_valid = isinstance(subdir, str) and subdir != ""
    exe_valid = isinstance(exe, str) and exe.endswith(".exe")
    logger.debug(f"Steam data: id={id}, subdir={subdir}, exe={exe}")
    logger.debug(
        f"Steam data validation: id_valid={id_valid}, subdir_valid={subdir_valid}, exe_valid={exe_valid}"
    )

    if id_valid and subdir_valid and exe_valid:
        return id, subdir, exe
    else:
        if not id_valid:
            logger.error(
                f'Steam ID for {game_info.get("display")} ("{id or "None"}") is not set or invalid.'
            )
        if not subdir_valid:
            logger.error(
                f'Steam subdirectory for {game_info.get("display")} ("{subdir or "None"}") is not set or invalid.'
            )
        if not exe_valid:
            logger.error(
                f'Executable for {game_info.get("display")} ("{exe or "None"}") is not set or invalid.'
            )

    match (id_valid, subdir_valid, exe_valid):
        case (False, False, False):
            return None, None, None
        case (True, True, False):
            return game_info.get("steam_id"), game_info.get("steam_subdirectory"), None
        case (True, False, True):
            return game_info.get("steam_id"), None, game_info.get("executable")
        case (False, True, True):
            return (
                None,
                game_info.get("steam_subdirectory"),
                game_info.get("executable"),
            )
        case _:
            logger.critical("Unexpected error in Steam data validation.")
            logger.critical("Aborting operation...")
            raise SystemExit(1)


def get_steam_library():
    from util.steam.find_library import get_libraries

    libraries = get_libraries()
    steam_id, steam_subdirectory, game_exe = get_steam_data()
    if steam_subdirectory and game_exe:
        logger.debug(
            f"Received valid Steam data: subdirectory={steam_subdirectory}, exe={game_exe}"
        )
    else:
        logger.critical(
            "Incomplete Steam data received. Cannot check for game installation."
        )
        logger.critical("Aborting operation...")
        raise SystemExit(1)

    for library in libraries:
        full_path = os.path.join(
            library, "steamapps", "common", steam_subdirectory, game_exe
        )
        logger.debug(f"Checking for game installation at: {full_path}")
        if os.path.exists(full_path):
            logger.info(f"Found game installation at: {full_path}")
            return library

    logger.warning(
        "Game not found in any Steam library. If installed, please ensure the game has been run at least once."
    )


def get_heroic_config():
    from util.heroic.find_library import get_heroic_data

    heroic_config = get_heroic_data()
    return heroic_config


def get_install_path():
    import util.variables as var

    steam_library = get_steam_library()
    heroic_config = get_heroic_config()
    heroic_config_valid = (
        any(heroic_config[i] is not None for i in (0, 2, 3, 4, 5))
        if heroic_config
        else False
    )

    if steam_library and heroic_config_valid:  # TODO
        logger.info("Both Steam and Heroic installations detected.")
        logger.error("Multi-launcher setups have not been implemented yet.")
        logger.critical("Aborting operation...")
        raise SystemExit(1)
    elif steam_library:
        var.launcher = "steam"
        var.game_install_path = os.path.join(
            steam_library,
            "steamapps",
            "common",
            var.game_info.get("steam_subdirectory"),
        )
        from util.wine.protontricks import get_prefix

        var.prefix = get_prefix(var.game_info.get("steam_id"))
    elif heroic_config_valid:
        var.launcher = "heroic"
        var.heroic_config = heroic_config
        var.heroic_runner = str(heroic_config[2])
        app = heroic_config[0]
        if heroic_config[2] == "gog":
            app = app[0]
        var.game_install_path = os.path.join(
            str(app), str(var.game_info.get("executable"))
        )
        var.prefix = heroic_config[5]
    else:
        var.launcher = None
        var.game_install_path = None
        logger.critical(
            "Could not determine game installation via Steam or Heroic. Please ensure the game is installed and has been run at least once."
        )
        logger.critical("Aborting operation...")
        raise SystemExit(1)

    logger.debug(f"Determined launcher: {var.launcher}")
    state.set_launcher(var.launcher)
    state.set_game_install_path(var.game_install_path)
    state.set_game_executable(var.game_info.get("executable"))
    state.set_launcher_ids(
        steam_id=var.game_info.get("steam_id"),
        gog_id=var.game_info.get("gog_id"),
        epic_id=var.game_info.get("epic_id"),
    )
    logger.debug(f"Determined game install path: {var.game_install_path}")


def main(game=None, custom_game_info_path: str = None):
    from util.variables import load_gameinfo, parameters

    load_gameinfo(
        game or parameters.get("game")
    ) if not custom_game_info_path else load_gameinfo(
        game or parameters.get("game"), custom_game_info_path
    )
    get_install_path()
    logger.success("Game information loaded successfully.")
