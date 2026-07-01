#!/usr/bin/env python3

from loguru import logger
from pathlib import Path
from typing import Optional
from step.external_resources import download_mod_organizer
from util import state_file as state, variables as var
from step.launch_opt import add_launch_opt, remove_launch_opt
from util.redirector.install import install as install_redirector
from util.nexus.install_handler import install as install_handler
from util.wine import protontricks, winetricks


def update_tricks():
    logger.info("Updating protontricks")
    try:
        if state.current_instance.launcher == "steam":
            protontricks.run(["--self-update"])
        else:
            winetricks.run(["--self-update"])
    except SystemExit as e:
        logger.warning(f"Failed to update tricks helper; continuing update: {e}")


def update(
    directory: Path,
    mo2_archive: Optional[Path] = None,
    mo2_checksum: Optional[str] = None,
):
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
            "mo2_archive": mo2_archive,
            "mo2_checksum": mo2_checksum,
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
        if mo2_archive:
            logger.info(
                "Instance is pinned, but a local archive was supplied; overriding the pin for this update."
            )
        else:
            logger.warning(
                "Instance is pinned. Please unpin the instance if you want to update it."
            )
            return

    logger.debug(f"Updating MO2 executable in directory: {directory}")
    download_mod_organizer()

    if mo2_archive:
        logger.info("Pinning instance to the supplied local archive build.")
        state.current_instance.pin = True
        state.write_state(add_current=True)

    update_tricks()

    install_redirector()
    install_handler()

    remove_launch_opt()
    add_launch_opt()
