#!/usr/bin/env python3

from pathlib import Path
import subprocess
import shutil
import os
from typing import List
from loguru import logger

exec = (
    shutil.which("winetricks")
    or Path("~/.cache/mo2-lint/downloads/winetricks").expanduser()
)


def run(prefix: Path, command: List[str]) -> List[str]:
    """
    Runs a winetricks command and captures its output.

    Parameters
    ----------
    prefix : Path
        The Wine prefix to use.
    command : List[str]
        The command arguments to pass to winetricks.

    Returns
    -------
    List[str]
        The output log lines from the winetricks command.
    """

    cmd = [str(exec), f"prefix={str(prefix)}"] + [str(c) for c in command]
    env = os.environ.copy()
    env.setdefault("WINEPREFIX", str(prefix))

    logger.debug(f"Running winetricks command: {' '.join(cmd)}")

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=env,
    )

    out_lines: List[str] = []
    if proc.stdout:
        for line in proc.stdout:
            line = line.strip()
            out_lines.append(line)
            logger.trace(line)

    exit_code = proc.wait()
    if exit_code == 0:
        logger.success("winetricks completed successfully.")
    else:
        logger.warning(f"winetricks exited with non-zero status: {exit_code}")

    return out_lines


def apply(prefix: Path, tricks: list):
    """
    Applies tricks to the specified prefix.

    Parameters
    ----------
    prefix : Path
        The Wine prefix to use.
    tricks : list
        The list of tricks to apply
    """

    logger.info(f"Applying tricks to prefix: {tricks}")
    run(prefix, tricks)


# TODO handle 'translation' of specific winetricks outputs
