#!usr/bin/env python3

from loguru import logger
from pathlib import Path
from typing import Optional
from util import variables as var, state_file as state
from util.state_file import set_index, InstanceData
from util.launch_opt import editor
from util.nexus.install_handler import install as install_handler
from util.symlink import create_mo2_symlink as symlink
from step.workarounds import apply_workarounds
from step.load_game_info import get_launcher, get_library
from step.external_resources import download
from step.configure_prefix import prompt as configure_prefix


def install(
    game: str,
    directory: Path,
    game_info_path: Optional[Path] = None,
    log_level: str = "INFO",
    script_extender: bool = False,
    plugin: Optional[tuple[str]] = (),
):
    var.set_parameters(
        {
            "game": game,
            "directory": directory,
            "game_info_path": game_info_path,
            "log_level": log_level,
            "script_extender": script_extender,
            "plugins": list(plugin),
        }
    )
    logger.debug(f"Starting installation with parameters: {var.input_params}")

    directory.mkdir(parents=True, exist_ok=True)
    logger.trace(f"Ensured installation directory exists: {directory}")

    if not state.match_instances(directory=directory):
        state.current_instance = InstanceData(
            index=-1,
            game=game,
            nexus_slug=var.game_info.nexus_slug,
            instance_path=directory,
            launcher=get_launcher(),
            launcher_ids=var.LauncherIDs.from_dict(var.game_info.launcher_ids),
            game_path=get_library(),
            game_executable=var.game_info.executable,
            script_extender=script_extender,
            plugins=list(plugin),
        )
        set_index()
    else:
        logger.critical(
            "An instance with the specified directory already exists. Aborting installation to prevent conflicts."
        )
        logger.warning(
            "Please choose a different installation directory or uninstall the existing instance before proceeding."
        )
        raise SystemExit(1)

    configure_prefix()
    download()
    install_handler()
    symlink(state.current_instance)

    # Add launch option to Steam
    if (
        state.current_instance.launcher == "steam"
        and state.current_instance.launcher_ids.steam
    ):
        appid = state.current_instance.launcher_ids.steam
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
        logger.info(f"Added launch option with index {launch_index} for appid {appid}")

    apply_workarounds()
