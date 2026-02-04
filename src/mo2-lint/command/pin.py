#!/usr/bin/env python3

from pathlib import Path
from util import state_file as state
from loguru import logger


def pin(directory: Path, pin: bool = True):
    """
    Pins the current MO2 version for the instance located at the given directory.
    """

    matched = state.match_instances(directory=directory)
    if not matched:
        raise ValueError(f"No instance found for directory: {directory}")
    elif len(matched) > 1:
        logger.critical(
            f"Multiple instances found for directory: {directory}. Cannot pin."
        )
        logger.error("Matched instances:")
        for key, value in matched.items():
            logger.error(f"  - {key}: {value}")
        logger.error("You should only specify directories for a single instance.")
        raise ValueError(f"Multiple instances found for directory: {directory}")
    state.current_instance = matched[0]
    logger.info(f"Pinning MO2 version for instance at {directory}")
    state.current_instance.pin = pin
    state.write_state(add_current=True)
