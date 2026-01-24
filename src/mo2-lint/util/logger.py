#!/usr/bin/env python3

from loguru import logger
from pathlib import Path
import sys
from datetime import datetime

timestamp: str = None
time_format = "{time:YYYY-MM-DD_HH-mm-ss}"


def remove_loggers():
    handler_ids = list(logger._core.handlers.keys())
    for hid in handler_ids:
        logger.remove(hid)


def persist_timestamp() -> str:
    global timestamp
    if not timestamp:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def add_loggers(log_level: str = "INFO", process: str = None, console_sink=None):
    persist_timestamp()

    format_str = (
        f"<green>{time_format}</green> | "
        + "<level>{level: <8}</level> | "
        + (f"{process.upper()} | " if process else "")
        + "{message}"
    )
    logger.add(
        sink=console_sink if console_sink is not None else sys.stdout,
        format=format_str,
        level=log_level,
    )

    logger.add(
        sink=Path(f"~/.cache/mo2-lint/logs/install.{timestamp}.log").expanduser(),
        format=f"{time_format} | "
        + " {level: <8} | "
        + (f"{process.upper()} | " if process else "")
        + " {module}:{function}:{line} - "
        + " {message} ",
        level="TRACE",
        rotation="10 MB",
        retention="7 days",
        compression="zip",
    )
