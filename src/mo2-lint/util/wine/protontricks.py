#!/usr/bin/env python3

from contextlib import contextmanager
from loguru import logger
from pathlib import Path
from protontricks.cli.main import main as pt
from typing import List
from util.logger import remove_loggers, add_loggers
import os
import re
import sys
import threading


def run(command: List[str]):
    """
    Runs a protontricks command and captures its output.

    Parameters
    ----------
    command : List[str]
        The command arguments to pass to protontricks.
    """

    args = ["--verbose"] + command

    logger.debug(f"Running protontricks command: {' '.join(args)}")

    if args != ["--verbose"]:
        with redirect_output_to_logger():
            try:
                pt(args)
            except SystemExit as e:
                if e.code != 0:
                    logger.exception(
                        f"Protontricks command failed with exit code {e.code}"
                    )
            except Exception as e:
                logger.exception(
                    f"Unexpected exception while running protontricks: {e}",
                    backtrace=True,
                    diagnose=True,
                )
            finally:
                logger.success(
                    f"Protontricks completed successfully with command: {' '.join(args)}"
                )
    else:
        logger.warning("No protontricks command provided, skipping.")
        return


def apply(id: int, tricks: List[str]):
    """
    Applies tricks to the specified prefix.

    Parameters
    ----------
    id : int
        The Proton prefix ID.
    tricks : List[str]
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


def get_prefix(id: int) -> Path:
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
            prefix = Path(line.strip())
            break

    if prefix and prefix.exists():
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
    add_loggers(process="protontricks", console_sink=original_stdout_file)

    def reader_thread():
        with os.fdopen(read_fd, "r", buffering=1) as reader:
            for line in reader:
                if line := line.rstrip("\n"):
                    output_lines.append(line)
                    logger.trace(line)
                    try:
                        log_translation(line)
                    except Exception:
                        logger.exception(
                            "Error translating protontricks log line",
                            backtrace=True,
                            diagnose=True,
                        )

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
        add_loggers()
