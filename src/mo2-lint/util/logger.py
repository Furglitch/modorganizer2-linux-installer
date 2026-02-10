#!/usr/bin/env python3

from datetime import datetime
from loguru import logger
from pathlib import Path
from util import variables as var
import sys

timestamp: str = None


def remove_loggers():
    """
    Removes existing loggers from loguru.
    """
    logger.trace("Removing existing loggers")
    handler_ids = list(logger._core.handlers.keys())
    for hid in handler_ids:
        logger.remove(hid)


def persist_timestamp() -> str:
    """
    Returns a timestamp created on the first call and persists it for future calls.

    Returns
    -------
    str
        A persisted timestamp string for log filenames.
    """
    global timestamp
    if not timestamp:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return timestamp


def add_loggers(log_level: str = None, process: str = "mo2-lint", console_sink=None):
    """
    Adds loggers to loguru, for file and console output.

    Parameters
    ----------
    log_level : str, optional
        Log level for console output. If None, uses the level from input parameters or defaults to "INFO".
    process : str, optional
        The name of the process to include in log messages.
    console_sink : optional
        The sink for console output. If None, uses sys.stdout.
    """

    time_format = "{time:YYYY-MM-DD HH:mm:ss}"

    log_format_str = (  # TIMESTAMP | [LEVEL] PROCESS : MODULE.FUNCTION@LINE | MESSAGE
        f"{time_format} | "
        "{level: <8} | "
        f"{process.upper()} : "
        "{module}.{function}@{line} | "
        "{message}"
    )

    console_format_str = (  # TIMESTAMP | [LEVEL] PROCESS | MESSAGE
        f"<green>{time_format}</green> | "
        + "<level>{level: <8}</level> | "
        + f"{process.upper()} | "
        + "{message}"
    )

    logger.add(
        sink=Path(
            f"~/.cache/mo2-lint/logs/install.{persist_timestamp()}.log"
        ).expanduser(),
        format=log_format_str,
        level="TRACE",
        rotation="10 MB",
        retention="7 days",
        compression="zip",
    )

    log_level = log_level or var.input_params.log_level or "INFO"
    logger.add(
        sink=console_sink if console_sink is not None else sys.stdout,
        format=console_format_str,
        level=log_level,
    )

    logger.trace(
        f"Added loggers with level {log_level} for console and TRACE for file output"
    )
