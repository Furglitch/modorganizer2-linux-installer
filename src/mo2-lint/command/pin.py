#!/usr/bin/env python3

from loguru import logger
from pathlib import Path
from util import state_file as state


def pin(directory: Path, pin: bool = True):
    """
    Pins or unpins the current MO2 version for the instance located at the given directory.
    """

    matched = state.match_instances(directory=directory, exact=True)
    if not matched:
        logger.error(f"No MO2 instance found in {directory}")
    elif len(matched) > 1:
        logger.critical(
            f"Multiple MO2 instances found in {directory}. Please specify the instance directory more precisely."
        )
        logger.error("Matched instances:")
        for key, value in matched.items():
            logger.error(f"  - {key}: {value}")
        logger.error(
            "Only one instance can be un-/pinned at a time. Please try again with a more specific directory."
        )
        raise SystemExit(1)

    logger.info(f"Setting pin for MO2 instance in directory: {directory}")
    state.current_instance = matched[0]
    state.current_instance.pin = pin
    state.write_state(add_current=True)
