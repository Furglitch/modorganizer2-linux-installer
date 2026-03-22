#!/usr/bin/env python3

from contextlib import contextmanager
from loguru import logger
from protontricks.cli.main import main as pt
from typing import List
from shared.logger import remove_loggers, add_loggers
import os
import re
import sys
import threading


def run(command: List[str]) -> List[str]:
    """
    Runs a protontricks command and captures its output.

    Parameters
    ----------
    command : List[str]
        The command arguments to pass to protontricks.

    Returns
    -------
    List[str]
        The output lines from the protontricks command.
    """

    args = ["--verbose"] + command
    logger.trace(f"Constructed protontricks command: {' '.join(args)}")

    output_lines = []
    if args != ["--verbose"]:
        with redirect_output_to_logger() as output_lines:
            try:
                pt(args)
            except SystemExit as e:
                if e.code != 0:
                    logger.error(
                        f"protontricks exited with code {e.code} for args: {args}"
                    )
            except Exception as e:
                logger.exception(f"Error running protontricks with args: {args} - {e}")
            finally:
                logger.success(f"Finished running protontricks with args: {args}")
    else:
        logger.debug("No protontricks command to run (only --verbose).")
    return output_lines


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
        logger.debug(translated)
        return
    if reg2:
        trick = reg2.group(1).strip()
        translated = f"Applying trick: '{trick}'"
        logger.debug(translated)
        return
    if reg3:
        dlls = reg3.group(1).strip()
        translated = f"Setting native DLLs: '{dlls}'"
        logger.debug(translated)
        return
    if reg4:
        pid_info = reg4.group(1).strip()
        translated = f"End of protontricks process (PID: {pid_info})"
        logger.debug(translated)
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
    add_loggers(
        script="nxm-handler", process="protontricks", console_sink=original_stdout_file
    )

    def reader_thread():
        with os.fdopen(read_fd, "r", buffering=1) as reader:
            for line in reader:
                if line := line.rstrip("\n"):
                    output_lines.append(line)
                    logger.trace(f"protontricks: {line}")
                    try:
                        log_translation(line)
                    except Exception as e:
                        logger.exception(
                            f"Error translating protontricks log line: {line}. {e}"
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
        add_loggers(script="nxm-handler", process="nxm-handler")
