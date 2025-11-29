#!/usr/bin/env python3

from pathlib import Path
import subprocess
import shutil
from loguru import logger

exe = shutil.which("protontricks") or "venv/bin/protontricks"


def run(command: list) -> str:
    cmd = [exe, "--verbose"] + command

    logger.debug(f"Running protontricks command: {' '.join(cmd)}")

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    out_lines = []
    if proc.stdout:
        for raw in proc.stdout:
            out_lines.append(raw)
            logger.trace(raw.strip())
            # TODO handle 'translation' of specific protontricks outputs

    ret = proc.wait()
    if ret == 0:
        logger.success("protontricks completed successfully.")
    else:
        logger.warning(f"protontricks exited with non-zero status: {ret}")
    return "".join(out_lines)


def apply(id: int, command: list):
    logger.info(f"Applying tricks to prefix: {command}")
    run([f"{id}", "-q", "--force"] + command)


def get_prefix(id: int):
    if str(id) not in run(["-l"]):
        logger.warn(f"Prefix for {id} does not exist.")
    else:
        out = run(["-c", "echo $WINEPREFIX", f"{id}"])
        for line in out.splitlines():
            if str(id) in line and "compatdata" in line:
                prefix = line.strip()
                break

    if Path(prefix.strip()).exists():
        logger.debug(f"Prefix for {id}: {prefix.strip()}")
    else:
        logger.error(f"Could not find a valid prefix directory for {id}.")
    return prefix
