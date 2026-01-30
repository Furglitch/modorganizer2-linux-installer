#!/usr/bin/env python3

from pathlib import Path
import subprocess
import shutil
import os
from typing import List, Optional
from loguru import logger
from util.logger import remove_loggers, add_loggers
import re

found_exec = shutil.which("winetricks") or "~/.cache/mo2-lint/downloads/winetricks"


def run(
    exec: Optional[Path | str] = found_exec,
    prefix: Path = None,
    command: List[str] = None,
) -> List[str]:
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

    # Convert executable to string, with absolute path
    if str(exec).startswith("/usr/bin"):
        if isinstance(exec, str):
            exec = str(Path(exec).name)
        elif isinstance(exec, Path):
            exec = str(exec.name)
    elif isinstance(exec, str):
        if not Path(exec).exists():
            logger.error(f"winetricks executable not found at: {exec}")
            return []
        exec = str(Path(exec).expanduser().resolve())
    elif isinstance(exec, Path):
        if not exec.exists():
            logger.error(f"winetricks executable not found at: {exec}")
            return []
        exec = str(exec.expanduser().resolve())

    cmd = [exec] + ["-q", "-f"] + [str(c) for c in command]
    env = os.environ.copy()
    env.setdefault("WINEPREFIX", str(prefix))

    logger.debug(f"Using WINEPREFIX: {env['WINEPREFIX']}")
    logger.debug(f"Running winetricks command: {' '.join(cmd)}")

    remove_loggers()
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=env,
    )
    add_loggers(process="winetricks")

    out_lines: List[str] = []
    if proc.stdout:
        for line in proc.stdout:
            line = line.strip()
            out_lines.append(line)
            logger.trace(f"winetricks: {line}")
            log_translation(line)

    exit_code = proc.wait()
    if exit_code == 0:
        logger.success("winetricks completed successfully.")
    else:
        logger.warning(f"winetricks exited with non-zero status: {exit_code}")

    remove_loggers()
    add_loggers()

    return out_lines


def apply(
    exec: Optional[Path | str] = found_exec, prefix: Path = None, tricks: list = None
):
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
    if not tricks:
        logger.info("No tricks to apply, skipping.")
        return
    run(exec, prefix, tricks)


def log_translation(input: str = None):
    """
    Translates protontricks log lines into more user-friendly messages and logs them.

    Parameters
    ----------
    input : str
        The log line to translate.
    """
    if not input:
        return

    reg1 = re.search(
        r"Executing w_do_call\s+(.*)", input
    )  # "Applying trick: '[trick]'"
    reg2 = re.search(
        r"Using native override for following DLLs:\s+(.*)", input
    )  # "Setting native DLLs: '[DLLs]'"

    if reg1:
        trick = reg1.group(1).strip()
        translated = f"Applying trick: '{trick}'"
        logger.info(translated)
        return
    if reg2:
        dlls = reg2.group(1).strip()
        translated = f"Setting native DLLs: '{dlls}'"
        logger.info(translated)
        return
