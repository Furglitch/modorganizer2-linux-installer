#!/usr/bin/env python3

from pathlib import Path
import subprocess
import shutil
from loguru import logger

exe = shutil.which("protontricks") or "venv/bin/protontricks"


def run(command: list) -> str:
    proc = subprocess.Popen(
        [exe, "--verbose"] + command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    out_lines = []
    if proc.stdout:
        for raw in proc.stdout:
            out_lines.append(raw)
            # Special handling can be added here:, e.g. `if "INFO" in raw: logger.info(raw.strip())`
    proc.wait()
    return "".join(out_lines)


def apply(id: int, command: list):
    logger.info(f"Applying tricks to prefix {id}: {command}")
    run([f"{id}", "-q", "--force"] + command)


def get_prefix(id: int):
    if str(id) not in run(["-l"]):
        logger.warn(f"Prefix for {id} does not exist.")
    else:
        prefix = run(["-c", "echo $WINEPREFIX", f"{id}"])

    if Path(prefix.strip()).exists():
        logger.info(f"Prefix for {id}: {prefix.strip()}")
    else:
        logger.error(f"Could not find a valid prefix directory for {id}.")
