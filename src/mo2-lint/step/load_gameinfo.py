#!/usr/bin/env python3

from loguru import logger
import os


def get_steam_data():
    from util.variables import game_info

    id = game_info["steam_id"]
    subdir = game_info["steam_subdirectory"]
    exe = game_info["executable"]
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
                f'Steam ID for {game_info["display"]} ("{id or "None"}") is not set or invalid.'
            )
        if not subdir_valid:
            logger.error(
                f'Steam subdirectory for {game_info["display"]} ("{subdir or "None"}") is not set or invalid.'
            )
        if not exe_valid:
            logger.error(
                f'Executable for {game_info["display"]} ("{exe or "None"}") is not set or invalid.'
            )

    match (id_valid, subdir_valid, exe_valid):
        case (False, False, False):
            return None, None, None
        case (True, True, False):
            return game_info["steam_id"], game_info["steam_subdirectory"], None
        case (True, False, True):
            return game_info["steam_id"], None, game_info["executable"]
        case (False, True, True):
            return None, game_info["steam_subdirectory"], game_info["executable"]
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

    # if steam_library and heroic_library: # TODO Handle multiple installs through different launchers
    if steam_library:
        var.launcher = "steam"
        var.game_install_path = os.path.join(
            steam_library, "steamapps", "common", var.game_info["steam_subdirectory"]
        )

    elif heroic_config:
        var.launcher = "heroic"
        var.heroic_config = heroic_config
        var.heroic_runner = str(heroic_config[2])
        app = heroic_config[0]
        if heroic_config[2] == "gog":
            app = app[0]
        var.game_install_path = os.path.join(str(app), str(var.game_info["executable"]))
    else:
        var.launcher = None
        var.game_install_path = None
        logger.critical(
            "Could not determine game installation via Steam or Heroic. Please ensure the game is installed and has been run at least once."
        )
        logger.critical("Aborting operation...")
        raise SystemExit(1)

    logger.debug(f"Determined launcher: {var.launcher}")
    logger.debug(f"Determined game install path: {var.game_install_path}")


def get_scriptextender_url():
    import util.variables as var

    if var.launcher == "heroic":
        type = var.heroic_runner
    else:
        type = "steam"

    if (
        var.game_info.get("script_extender") is None
        or var.game_info.get("script_extender", {}).get(type) is None
    ):
        logger.warning(f"No Script Extender information available for {var.launcher}.")
        return

    var.scriptextender_version = (
        var.game_info.get("script_extender", {})
        .get(type, {})
        .get("resource", {})
        .get("version")
    )

    url = (
        var.game_info.get("script_extender", {})
        .get(type, {})
        .get("resource", {})
        .get("url")
    )
    mod_id = (
        var.game_info.get("script_extender", {})
        .get(type, {})
        .get("resource", {})
        .get("mod_id")
    )
    file_id = (
        var.game_info.get("script_extender", {})
        .get(type, {})
        .get("resource", {})
        .get("file_id")
    )

    if url:
        var.scriptextender_url = url
        logger.debug(f"Determined Script Extender URL: {var.scriptextender_url}")
    elif mod_id and file_id:
        var.scriptextender_nxm_modid = mod_id
        var.scriptextender_nxm_fileid = file_id
        logger.debug(
            f"Determined Script Extender Nexus Mod ID: {var.scriptextender_nxm_modid} - File ID: {var.scriptextender_nxm_fileid}"
        )
    else:
        var.scriptextender_url = None
        var.scriptextender_nxm_modid = None
        var.scriptextender_nxm_fileid = None
        logger.warning(
            f"Unable to find Script Extender download URL or Nexus Mod IDs for {var.launcher}."
        )


def main():
    from util.variables import load_gameinfo, parameters

    load_gameinfo(parameters["game"])
    get_install_path()
    if parameters["script_extender"] is True:
        get_scriptextender_url()
    logger.success("Game information loaded successfully.")
