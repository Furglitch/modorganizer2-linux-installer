#!/usr/bin/env python3

from contextlib import contextmanager
import os
from pathlib import Path
import sys
from loguru import logger
from util.logger import remove_loggers, add_loggers
from util.variables import input
from protontricks.cli.main import main as pt
from typing import List
import re
import threading


def run(command: list) -> List[str]:
    """
    Runs a protontricks command and captures its output.

    Parameters
    ----------
    command : list
        The command arguments to pass to protontricks.

    Returns
    -------
    List[str]
        The output log lines from the protontricks command.
    """

    args = ["--verbose"] + [str(c) for c in command]

    logger.debug(f"Running protontricks command: {' '.join(args)}")

    with redirect_output_to_logger() as output_lines:
        try:
            pt(args)
        except SystemExit as e:
            if e.code != 0:
                logger.error(f"Protontricks command failed with exit code {e.code}")

    return output_lines


def apply(id: int, tricks: list):
    """
    Applies tricks to the specified prefix.

    Parameters
    ----------
    id : int
        The Proton prefix ID.
    tricks : list
        The list of tricks to apply
    """

    logger.info(f"Applying tricks to prefix: {tricks}")
    run([f"{id}", "-q", "--force"] + tricks)


def check_prefix(id: int) -> bool:
    """
    Checks if a Proton prefix exists for the given ID.

    Parameters
    ----------
    id : int
        The Proton prefix ID.

    Returns
    -------
    bool
        True if the prefix exists, False otherwise.
    """
    listing = run(["-l"]) or []
    exists = any(str(id) in line for line in listing)
    if exists:
        logger.debug(f"Prefix for {id} exists.")
    else:
        logger.warning(f"Prefix for {id} does not exist.")
    return exists


def get_prefix(id: int) -> str | None:
    """
    Retrieves the Proton prefix path for the given ID if it exists.

    Parameters
    ----------
    id : int
        The Proton prefix ID.

    Returns
    -------
    str
        The path to the Proton prefix if it exists, otherwise None.
    """
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
        r"Attempting to run command\s+(.*)", input
    )  # "Running: '[command]'"
    reg2 = re.search(
        r"Executing w_do_call\s+(.*)", input
    )  # "Applying trick: '[trick]'"
    reg3 = re.search(
        r"Using native override for following DLLs:\s+(.*)", input
    )  # "Setting native DLLs: '[DLLs]'"
    reg4 = re.search(
        r"Terminating launcher process\s+(.*)", input
    )  # "End of protontricks process (PID: [pid])"

    if reg1:
        cmd = reg1.group(1).strip()
        if cmd.startswith("[") and cmd.endswith("]"):
            cmd = cmd[1:-1].strip()
            cmd = cmd.replace("'", "").replace(",", "")
        translated = f"Running: '{cmd}'"
        logger.info(translated)
        return
    if reg2:
        trick = reg2.group(1).strip()
        translated = f"Applying trick: '{trick}'"
        logger.info(translated)
        return
    if reg3:
        dlls = reg3.group(1).strip()
        translated = f"Setting native DLLs: '{dlls}'"
        logger.info(translated)
        return
    if reg4:
        pid_info = reg4.group(1).strip()
        translated = f"End of protontricks process (PID: {pid_info})"
        logger.info(translated)
        return


@contextmanager
def redirect_output_to_logger():
    """
    Context manager to redirect stdout and stderr to the logger.
    """

    read_fd, write_fd = os.pipe()
    output_lines = []

    original_stdout_fd = os.dup(sys.stdout.fileno())
    original_stderr_fd = os.dup(sys.stderr.fileno())
    original_stdout_file = os.fdopen(original_stdout_fd, "w", buffering=1)

    remove_loggers()
    add_loggers(input.log_level, "protontricks", console_sink=original_stdout_file)

    def reader_thread():
        with os.fdopen(read_fd, "r", buffering=1) as reader:
            for line in reader:
                if line := line.rstrip("\n"):
                    output_lines.append(line)
                    print(line)
                    logger.trace(line)
                    log_translation(line)

    threading.Thread(target=reader_thread, daemon=True).start()

    try:
        os.dup2(write_fd, sys.stdout.fileno())
        os.dup2(write_fd, sys.stderr.fileno())

        yield output_lines

    finally:
        os.dup2(original_stdout_fd, sys.stdout.fileno())
        os.dup2(original_stderr_fd, sys.stderr.fileno())
        os.close(write_fd)
        os.close(original_stderr_fd)

        remove_loggers()
        original_stdout_file.close()
        add_loggers(input.log_level, "MO2-LINT")
