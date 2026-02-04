#!/usr/bin/env python3

from pathlib import Path
from util import state_file as state
from loguru import logger
from step.external_resources import download_mod_organizer
from util.redirector.install import install as install_redirector


def update(directory: Path):
    """
    Updates the MO2 instance located at the given directory.
    """

    matched = state.match_instances(directory=directory)
    if not matched:
        raise ValueError(f"No instance found for directory: {directory}")
    elif len(matched) > 1:
        logger.critical(
            f"Multiple instances found for directory: {directory}. Cannot update."
        )
        logger.error("Matched instances:")
        for key, value in matched.items():
            logger.error(f"  - {key}: {value}")
        logger.error("You should only specify directories for a single instance.")
        raise ValueError(f"Multiple instances found for directory: {directory}")
    state.current_instance = matched[0]
    logger.info(f"Updating at {directory}")

    download_mod_organizer()
    install_redirector()
