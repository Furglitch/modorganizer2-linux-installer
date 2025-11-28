#!/usr/bin/env python3

from pathlib import Path
import subprocess
import shutil
from loguru import logger

pt = shutil.which("protontricks") or "venv/bin/protontricks"


def run(command: list) -> str:
    proc = subprocess.run([pt, "--verbose"] + command, capture_output=True, text=True)
    return proc.stdout


def apply(id: int, command: list):
    logger.info(run([f"{id}", "-q", "--force"] + command))


def get_prefix(id: int):
    if str(id) not in run(["-l"]):
        logger.warn(f"Prefix for {id} does not exist.")
    else:
        prefix = run(["-c", "echo $WINEPREFIX", f"{id}"])

    if Path(prefix.strip()).exists():
        logger.info(f"Prefix for {id}: {prefix.strip()}")
    else:
        logger.error(f"Could not find a valid prefix directory for {id}.")
