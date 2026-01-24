#!/usr/bin/env python3

from loguru import logger
from pathlib import Path
import sys
from datetime import datetime

_filename_timestamp: str = None
_message_time_placeholder = "{time:YYYY-MM-DD_HH-mm-ss}"


def remove_loggers():
    print("Removing all loggers")
    handler_ids = list(logger._core.handlers.keys())
    for hid in handler_ids:
        logger.remove(hid)


def _ensure_filename_timestamp() -> str:
    global _filename_timestamp
    if not _filename_timestamp:
        _filename_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return _filename_timestamp


def add_loggers(log_level: str = "INFO", process: str = None, console_sink=None):
    print(f"Setting up loggers with level: {log_level}")
    if process:
        print(f"Process identifier: {process}")

    filename_ts = _ensure_filename_timestamp()

    format_str = (
        f"<green>{_message_time_placeholder}</green> | "
        "<level>{level: <8}</level> | "
        + (f"{process.upper()} | " if process else "")
        + "{message}"
    )
    logger.add(
        sink=console_sink if console_sink is not None else sys.stdout,
        format=format_str,
        level=log_level,
    )

    logger.add(
        sink=Path(f"~/.cache/mo2-lint/logs/install.{filename_ts}.log").expanduser(),
        format=f"{_message_time_placeholder} | "
        " {level: <8} | "
        " {module}:{function}:{line} - "
        " {message} ",
        level="TRACE",
        rotation="10 MB",
        retention="7 days",
        compression="zip",
    )
