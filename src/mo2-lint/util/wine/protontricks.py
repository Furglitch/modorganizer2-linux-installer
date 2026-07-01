#!/usr/bin/env python3

from contextlib import contextmanager
from loguru import logger
from pathlib import Path
from protontricks.cli.main import main as pt
from typing import List
from shared.logger import remove_loggers, add_loggers
from util import variables as var
import os
import re
import sys
import threading


class ProtontricksOutput(list):
    """Captured protontricks output with the most recent error line."""

    def __init__(self, *args):
        super().__init__(*args)
        self.error_message: str | None = None


def error_from_line(line: str) -> str | None:
    ignored_patterns = (
        r"^warning: WINE is .*, which is neither on the path nor an executable file$",
    )
    for pattern in ignored_patterns:
        if re.search(pattern, line):
            return None

    error_patterns = (
        r"protontricks \(ERROR\):\s*(.*)",
        r"^(Steam app with the given app ID could not be found\..*)$",
        r"^(.+: error: .*)$",
        r"^(warning: Unknown file arch of .*)$",
        r"^([A-Za-z_][\w.]*[Ee]rror: .*)$",
        r"^([A-Za-z_][\w.]*[Ee]xception: .*)$",
        r"^([Ee]rror: .*)$",
        r"(?i)^(traceback .*)$",
        r"(?i)^(.*\b(?:failed|failure|fatal|invalid|not found|could not|unable to|isn't installed|is not installed|aborted|aborting)\b.*)$",
    )
    for pattern in error_patterns:
        if match := re.search(pattern, line):
            return match.group(1).strip()
    return None


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

    args = ["--verbose", "--no-bwrap"] + command
    logger.trace(f"Constructed protontricks command: {' '.join(args)}")

    output_lines = ProtontricksOutput()
    if args != ["--verbose"]:
        exit_code = None
        unexpected_error = None
        with redirect_output_to_logger() as output_lines:
            try:
                pt(args)
            except SystemExit as e:
                if e.code not in (0, None):
                    exit_code = e.code if isinstance(e.code, int) else 1
            except Exception as e:
                unexpected_error = e
            finally:
                logger.debug(f"Finished running protontricks with args: {args}")

        if exit_code is not None:
            error_message = output_lines.error_message or "Unknown protontricks error"
            logger.error(
                f"protontricks exited with code {exit_code} for args: {args}: {error_message}"
            )
            raise SystemExit(exit_code)

        if unexpected_error is not None:
            error_message = output_lines.error_message or str(unexpected_error)
            logger.error(
                f"Error running protontricks with args: {args}: {error_message}"
            )
            raise SystemExit(1) from unexpected_error

        logger.success(f"protontricks command completed successfully: {args}")
    else:
        logger.debug("No protontricks command to run (only --verbose).")
    return output_lines


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

    logger.debug(f"Applying tricks to prefix ID {id}: {tricks}")
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
        logger.trace(f"Found Proton prefix with ID {id} in listing.")
    else:
        logger.trace(f"Proton prefix with ID {id} does not exist.")
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
    Path
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
        logger.trace(f"Proton prefix path for ID {id}: {prefix}")
        return prefix
    else:
        logger.warning(f"Proton prefix path for ID {id} not found.")
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
    output_lines = ProtontricksOutput()

    original_stdout_fd = os.dup(sys.stdout.fileno())
    original_stderr_fd = os.dup(sys.stderr.fileno())
    original_stdout_file = os.fdopen(original_stdout_fd, "w", buffering=1)

    level = var.input_params.log_level if var.input_params else "INFO"
    remove_loggers()
    add_loggers(
        log_level=level,
        script="mo2-lint",
        process="protontricks",
        console_sink=original_stdout_file,
    )

    def reader_thread():
        with os.fdopen(read_fd, "r", buffering=1) as reader:
            for line in reader:
                if line := line.rstrip("\n"):
                    output_lines.append(line)
                    if error_message := error_from_line(line):
                        output_lines.error_message = error_message
                    logger.trace(f"protontricks: {line}")
                    try:
                        log_translation(line)
                    except Exception:
                        logger.exception(
                            f"Error translating protontricks log line: {line}."
                        )

    reader = threading.Thread(target=reader_thread, daemon=True)
    reader.start()

    try:
        os.dup2(write_fd, sys.stdout.fileno())
        os.dup2(write_fd, sys.stderr.fileno())

        yield output_lines

    finally:
        sys.stdout.flush()
        sys.stderr.flush()
        os.dup2(original_stdout_fd, sys.stdout.fileno())
        os.dup2(original_stderr_fd, sys.stderr.fileno())
        os.close(write_fd)
        os.close(original_stderr_fd)

        reader.join()

        remove_loggers()
        original_stdout_file.close()
        add_loggers(log_level=level, script="mo2-lint", process="installer")
