#!/usr/bin/env python3

from loguru import logger
from util import state_file as state
from util import variables as var
from util.launch_opt.editor import add_launch_option, remove_launch_option


def add_launch_opt():
    launcher = state.current_instance.launcher
    game_id = getattr(state.current_instance.launcher_ids, launcher, None)

    if launcher and game_id:
        if launcher == "steam":
            label = "MO2 " + var.game_info.display_name
        else:
            label = "Launch Mod Organizer"

        add_launch_option(
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
            proton_wrapper=state.current_instance.proton_wrapper,
        )

        if launcher == "steam":
            logger.info(f"Added compatibility tool for {launcher} game ID {game_id}")
        else:
            logger.info(f"Added launch option for {launcher} game ID {game_id}")
    else:
        logger.warning(
            f"Launcher '{launcher}' is not supported for launcher configuration, or launcher ID is missing"
        )


def remove_launch_opt():
    launcher = state.current_instance.launcher
    game_id = getattr(state.current_instance.launcher_ids, launcher, None)
    if launcher and game_id:
        if launcher == "steam":
            remove_launch_option(
                launcher=launcher,
                game_id=game_id,
                proton_wrapper=state.current_instance.proton_wrapper,
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
        if launcher == "steam":
            logger.info(f"Removed compatibility tool for {launcher} game ID {game_id}")
        else:
            logger.info(f"Removed launch option for {launcher} game ID {game_id}")
    else:
        logger.warning(
            f"Launcher '{launcher}' is not supported for launcher configuration, or launcher ID is missing"
        )
