#!usr/bin/env python3

from loguru import logger
from pathlib import Path
from typing import Optional
from util import variables as var, state_file as state
from util.state_file import set_index, InstanceData
from util.redirector.install import install as install_redirector
from util.nexus.install_handler import install as install_handler
from step.workarounds import apply_workarounds
from step.load_game_info import get_launcher, get_library
from step.external_resources import download
from step.configure_prefix import prompt as configure_prefix
from step.launch_opt import add_launch_opt


def install(
    game: str,
    directory: Path,
    game_info_path: Optional[Path] = None,
    log_level: str = "INFO",
    script_extender: bool = False,
    plugin: Optional[tuple[str]] = (),
    launcher: Optional[str] = None,
    mo2_archive: Optional[Path] = None,
    mo2_checksum: Optional[str] = None,
):
    var.set_parameters(
        {
            "game": game,
            "directory": directory,
            "game_info_path": game_info_path,
            "log_level": log_level,
            "script_extender": script_extender,
            "plugins": list(plugin),
            "mo2_archive": mo2_archive,
            "mo2_checksum": mo2_checksum,
        }
    )
    logger.debug(f"Starting installation with parameters: {var.input_params}")

    directory.mkdir(parents=True, exist_ok=True)
    logger.debug(f"Ensured installation directory exists: {directory}")

    if not state.match_instances(directory=directory):
        launcher = get_launcher(launcher)
        executable = (
            var.game_info.executable.get(launcher)
            if isinstance(var.game_info.executable, dict)
            else var.game_info.executable
        )
        state.current_instance = InstanceData(
            index=-1,
            game=game,
            nexus_slug=var.game_info.nexus_slug,
            instance_path=directory,
            pin=mo2_archive is not None,
            launcher=launcher,
            launcher_ids=var.LauncherIDs.from_dict(var.game_info.launcher_ids),
            game_path=get_library(),
            game_executable=executable,
            script_extender=None,
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
    logger.info("Prefix configuration completed")

    download()
    logger.info("Download phase completed")

    install_handler()
    logger.info("Installation handler completed")

    install_redirector()
    logger.info("Redirector installation completed")

    add_launch_opt()
    logger.info("Launch options configured")

    apply_workarounds()
    logger.info("Workarounds applied")
    logger.success("Installation completed successfully")
