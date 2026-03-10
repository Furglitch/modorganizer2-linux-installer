#!/usr/bin/env python3

from loguru import logger
from util import state_file as state, variables as var
from util.launch_opt.editor import add_launch_option, remove_launch_option


def add_launch_opt():
    launcher = state.current_instance.launcher
    game_id = getattr(state.current_instance.launcher_ids, launcher, None)
    if launcher and game_id:
        launch_index = add_launch_option(
            launcher=launcher,
            game_id=game_id,
            executable="mo2-redirector.exe",
            arguments=var.game_info.launch_options.get("arguments", [])
            if var.game_info.launch_options
            else [],
            label="Launch Mod Organizer",
            opt_type=var.game_info.launch_options.get("type", "none")
            if var.game_info.launch_options
            else "none",
            oslist=var.game_info.launch_options.get("oslist", None)
            if var.game_info.launch_options
            else None,
            osarch=var.game_info.launch_options.get("osarch", None)
            if var.game_info.launch_options
            else None,
        )
        if launcher == "steam" and launch_index is not None:
            state.current_instance.launch_option_index = launch_index
        logger.info(f"Added launch option for {launcher} game ID {game_id}")
    else:
        logger.warning(
            f"Launcher '{launcher}' is not supported for launch options, or launcher ID is missing"
        )


def remove_launch_opt():
    launcher = state.current_instance.launcher
    game_id = getattr(state.current_instance.launcher_ids, launcher, None)
    if launcher and game_id:
        if (
            launcher == "steam"
            and state.current_instance.launch_option_index is not None
        ):
            remove_launch_option(
                launcher=launcher,
                game_id=game_id,
                index=state.current_instance.launch_option_index,
            )
        elif launcher == "epic":
            remove_launch_option(
                launcher=launcher,
                game_id=game_id,
                label="Launch Mod Organizer",
            )
        logger.info(f"Removed launch option for {launcher} game ID {game_id}")
    else:
        logger.warning(
            f"Launcher '{launcher}' is not supported for launch options, or launcher ID is missing"
        )
