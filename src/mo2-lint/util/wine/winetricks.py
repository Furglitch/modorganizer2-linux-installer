#!/usr/bin/env python3

from loguru import logger
from pathlib import Path
from typing import List
from shared.logger import remove_loggers, add_loggers
from util.download import download_dir
import os
import re
import shutil
import subprocess

cached_winetricks = download_dir / "winetricks"
found_exec = shutil.which("winetricks")
# Try to use $WINETRICKS, only if it provides a file
winetricks_path = os.environ.get("WINETRICKS")
if winetricks_path:
    winetricks_path = Path(winetricks_path).expanduser()
elif found_exec:
    winetricks_path = Path(found_exec)
else:
    winetricks_path = cached_winetricks


def run(
    exe: Path | str = winetricks_path,
    prefix: Path | str = None,
    command: List[str] = [],
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
        The output lines from the winetricks command.
    """

    if not isinstance(exe, (str, Path)):
        raise TypeError("exe parameter must be a Path or string")
    if not isinstance(prefix, (str, Path)):
        raise TypeError("prefix parameter must be a Path or string")
    if not isinstance(command, list):
        raise TypeError("command parameter must be a list")
    if isinstance(exe, str):
        exe = Path(exe)
    exe = exe.expanduser().resolve()
    if isinstance(prefix, str):
        prefix = Path(prefix)
    prefix = prefix.expanduser().resolve()

    if exe.is_relative_to("/usr/bin"):
        # If referring to winetricks by bare name when possible is correct behavior, then it should
        # probably be done whenever bool(found_exec), not just when it was found in /usr/bin?
        exe = str(exe.name)
    else:
        if not exe.exists():
            logger.error(f"Winetricks executable not found at specified path: {exe}")
            return []
        exe = str(exe)
    logger.info(f"Using winetricks executable: {exe}")

    cmd = ["-q", "-f"] + command  # -q for unattended, -f to force
    logger.debug(f"Constructed winetricks command: {' '.join(cmd)}")
    cmd.insert(exe)
    env = os.environ.copy()
    env.setdefault("WINEPREFIX", str(prefix))
    logger.trace(f"Using Wine prefix: {prefix}")

    remove_loggers()
    add_loggers(script="mo2-lint", process="winetricks")
    output_lines = []

    if not cmd == [exe, "-q", "-f"]:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            env=env,
        )
    else:
        logger.warning("No winetricks command provided, skipping execution.")
        return output_lines

    if proc.stdout:
        for line in proc.stdout:
            line = line.strip()
            log_translation(line)
            logger.trace(f"winetricks: {line}")
            output_lines.append(line)

    exit_code = proc.wait()
    if exit_code == 0:
        logger.success("winetricks command completed successfully.")
    else:
        logger.error(f"winetricks command failed with exit code: {exit_code}")

    remove_loggers()
    add_loggers(script="mo2-lint", process="installer")
    return output_lines


def apply(
    prefix: Path,
    tricks: List[str],
):
    """
    Applies tricks to the specified prefix.

    Parameters
    ----------
    prefix : Path
        The Wine prefix to use.
    tricks : List[str]
        The list of tricks to apply
    """

    if not tricks:
        logger.warning("No tricks provided to apply, skipping winetricks execution.")
        return
    logger.info(f"Applying tricks to prefix with winetricks: {tricks}")
    run(prefix=prefix, tricks=tricks)


def log_translation(input: str = None):
    """
    Translates winetricks log lines into more user-friendly messages and logs them.

    Parameters
    ----------
    input : str
        The log line to translate.
    """
    if not input:
        return

    # "Applying trick: '[trick]'"
    reg1 = re.search(r"Executing w_do_call\s+(.*)", input)
    # "Setting native DLLs: '[DLLs]'"
    reg2 = re.search(r"Using native override for following DLLs:\s+(.*)", input)

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
