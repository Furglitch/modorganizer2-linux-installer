#!/usr/bin/env python3

from loguru import logger
from pathlib import Path
from step.external_resources import download_mod_organizer
from util import state_file as state, variables as var
from util.symlink import create_mo2_symlink as symlink
from util.launch_opt import editor


def update(directory: Path):
    """
    Updates the MO2 instance located at the given directory and refreshes the launch option.
    """

    var.set_parameters(
        {
            "game": "placeholder",
            "directory": directory,
            "game_info_path": None,
            "log_level": None,
            "script_extender": None,
            "plugins": [],
        }
    )

    matched = state.match_instances(directory=directory, exact=True)
    if not matched:
        logger.error(f"No MO2 instance found in {directory}")
    elif len(matched) > 1:
        logger.critical(
            f"Multiple MO2 instances found in {directory}. Please specify the instance directory more precisely."
        )
        logger.error("Matched instances:")
        for item in matched:
            logger.error(f"  - {item}")
        logger.error(
            "Only one instance can be updated at a time. Please try again with a more specific directory."
        )
        raise SystemExit(1)

    logger.info(f"Updating MO2 instance in directory: {directory}")
    state.current_instance = matched[0]
    var.load_game_info(state.current_instance.game)

    if state.current_instance.pin is True:
        logger.warning(
            "Instance is pinned. Please unpin the instance if you want to update it."
        )
        return

    logger.debug(f"Updating MO2 executable in directory: {directory}")
    download_mod_organizer()

    # Update symlink and launch option
    symlink(state.current_instance)

    # Update launch option if using Steam
    if (
        state.current_instance.launcher == "steam"
        and state.current_instance.launcher_ids.steam
    ):
        appid = state.current_instance.launcher_ids.steam

        # Remove old launch option if it exists
        if state.current_instance.launch_option_index is not None:
            editor.remove_internal(
                appid=appid,
                index=state.current_instance.launch_option_index,
                no_backup=False,
            )
            logger.debug(
                f"Removed old launch option with index {state.current_instance.launch_option_index}"
            )

        # Determine launch option attributes from game_info
        # Add new launch option
        launch_index = editor.add_internal(
            appid=appid,
            executable="ModOrganizer.exe",
            arguments=var.game_info.launch_options.get("arguments", [])
            if var.game_info.launch_options
            else [],
            label="Launch Mod Organizer",
            opt_type=var.game_info.launch_options.get("type", "default")
            if var.game_info.launch_options
            else "default",
            oslist=var.game_info.launch_options.get("oslist", None)
            if var.game_info.launch_options
            else None,
            osarch=var.game_info.launch_options.get("osarch", None)
            if var.game_info.launch_options
            else None,
        )
        state.current_instance.launch_option_index = launch_index
        logger.info(
            f"Updated launch option with index {launch_index} for appid {appid}"
        )
