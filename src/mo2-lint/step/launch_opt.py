#!/usr/bin/env python3

from loguru import logger
from util import state_file as state, variables as var
from util.launch_opt.editor import add_launch_option, remove_launch_option


def add_launch_opt():
    launcher = state.current_instance.launcher
    game_id = getattr(state.current_instance.launcher_ids, launcher, None)
    if launcher and game_id:
        label = "Mod Organizer"
        if not launcher == "steam":
            label = "Launch " + label
        launch_index = add_launch_option(
            launcher=launcher,
            game_id=game_id,
            executable="mo2-redirector.exe",
            arguments=var.game_info.launch_options.get("arguments", [])
            if var.game_info.launch_options
            and "arguments" in var.game_info.launch_options
            else [],
            label=var.game_info.launch_options.get("label", label)
            if var.game_info.launch_options and "label" in var.game_info.launch_options
            else label,
            game_path=str(state.current_instance.game_path)
            if state.current_instance.game_path
            else None,
            opt_type=var.game_info.launch_options.get("type", "OPTION3")
            if var.game_info.launch_options and "type" in var.game_info.launch_options
            else "OPTION3",
            oslist=var.game_info.launch_options.get("oslist", None)
            if var.game_info.launch_options and "oslist" in var.game_info.launch_options
            else None,
            osarch=var.game_info.launch_options.get("osarch", None)
            if var.game_info.launch_options and "osarch" in var.game_info.launch_options
            else None,
        )
        if launcher == "steam" and launch_index is not None:
            state.current_instance.launch_option_index = launch_index
            # Store the launch option type for Steam URL protocol
            state.current_instance.launch_option_type = (
                var.game_info.launch_options.get("type", "OPTION3")
                if var.game_info.launch_options
                else "OPTION3"
            )
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
        elif launcher == "gog":
            remove_launch_option(
                launcher=launcher,
                game_id=game_id,
                game_path=str(state.current_instance.game_path)
                if state.current_instance.game_path
                else None,
                label="Launch Mod Organizer",
            )
        logger.info(f"Removed launch option for {launcher} game ID {game_id}")
    else:
        logger.warning(
            f"Launcher '{launcher}' is not supported for launch options, or launcher ID is missing"
        )
