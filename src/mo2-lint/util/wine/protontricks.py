#!/usr/bin/env python3

import os
from pathlib import Path
import sys
from loguru import logger
from protontricks.cli.main import main as pt
from typing import List
import threading


def run(command: list) -> List[str]:
    args = ["--verbose"] + [str(c) for c in command]
    read_fd, write_fd = os.pipe()
    output_lines = []

    original_stdout_fd = os.dup(sys.stdout.fileno())
    original_stderr_fd = os.dup(sys.stderr.fileno())
    original_stdout_file = os.fdopen(original_stdout_fd, "w", buffering=1)

    handler_ids = list(logger._core.handlers.keys())
    for hid in handler_ids:
        logger.remove(hid)
    new_handler_id = logger.add(
        original_stdout_file, format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
    )

    def reader_thread():
        with os.fdopen(read_fd, "r", buffering=1) as reader:
            for line in reader:
                if line := line.rstrip("\n"):
                    output_lines.append(line)
                    logger.info(line)

    threading.Thread(target=reader_thread, daemon=True).start()

    try:
        os.dup2(write_fd, sys.stdout.fileno())
        os.dup2(write_fd, sys.stderr.fileno())
        logger.debug(f"Running protontricks command: {' '.join(args)}")
        pt(args)
    except SystemExit as e:
        if e.code != 0:
            logger.error(f"Protontricks command failed with exit code {e.code}")
    finally:
        os.dup2(original_stdout_fd, sys.stdout.fileno())
        os.dup2(original_stderr_fd, sys.stderr.fileno())
        os.close(write_fd)
        os.close(original_stderr_fd)

    logger.remove(new_handler_id)
    original_stdout_file.close()

    logger.add(  # TODO refactor to helper function for use with __init__
        sys.stdout,
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | {message}",
    )
    filename = Path(
        "~/.cache/mo2-lint/logs/install.{time:YYYY-MM-DD_HH-mm-ss}.log"
    ).expanduser()
    logger.add(
        filename,
        level="TRACE",
        rotation="10 MB",
        retention="7 days",
        compression="zip",
    )

    return output_lines


def apply(id: int, command: list):
    logger.info(f"Applying tricks to prefix: {command}")
    run([f"{id}", "-q", "--force"] + command)


def check_prefix(id: int) -> bool:
    listing = run(["-l"]) or []
    exists = any(str(id) in line for line in listing)
    if exists:
        logger.debug(f"Prefix for {id} exists.")
    else:
        logger.warning(f"Prefix for {id} does not exist.")
    return exists


def get_prefix(id: int):
    if not check_prefix(id):
        return None

    out_lines = run(["-c", "echo $WINEPREFIX", str(id)]) or []
    prefix = None
    for line in out_lines:
        if str(id) in line and "compatdata" in line:
            prefix = line.strip()
            break

    if prefix and Path(prefix).exists():
        logger.debug(f"Prefix for {id}: {prefix}")
    else:
        logger.error(f"Could not find a valid prefix directory for {id}.")
    return prefix
