#!/usr/bin/env python3

from pathlib import Path
from loguru import logger
from logger import add_loggers, remove_loggers
import os
import sys

separator: str = os.path.sep
instance_path_file: Path = Path("modorganizer2" + separator + "instance_path.txt")


def can_execute(exe: Path) -> bool:
    """
    Checks if the given path is a file and is executable.

    Parameters:
    -----------
    exe : Path
        Path to the executable file

    Returns:
    --------
    bool
        True if exe exists and is executable
    """
    if not exe.is_file():
        logger.error(f"File not found: {exe}")
        return False

    return (
        os.access(exe, os.R_OK)
        if str(exe).lower().endswith(".exe")
        else os.access(exe, os.X_OK)
    )


def execute(exe: Path, args: list[str]) -> int:
    """
    Executes the given executable with the provided arguments.
    If the executable is a Windows .exe file, it will attempt to run it using Wine.

    Parameters:
    -----------
    exe : Path
        Path to the executable file
    args : list[str]
        List of arguments to pass to the executable

    Returns:
    --------
    int
        Exit status of the executed process
    """
    exe_str = str(exe)

    if exe_str.lower().endswith(".exe"):
        wine = os.getenv("WINE", "wine64")
        try:
            os.execlp(wine, wine, exe_str, *(args if args else []))
            return 0
        except Exception as e:
            logger.error(f"Failed to execute {exe_str} with {wine}: {e}")
            return 1

    try:
        os.execl(exe_str, exe_str, *(args if args else []))
        return 0
    except Exception as e:
        logger.error(f"Failed to execute {exe_str}: {e}")
        return 1


def get_instance_path(path_file: Path) -> Path:
    """
    Reads the instance path from the specified file.

    Parameters:
    -----------
    path_file : Path
        Path to the file containing the instance path

    Returns:
    --------
    Path
        The instance path read from the file, or None if an error occurred
    """

    if not path_file.is_file():
        logger.error(f"Instance path file not found: {path_file}")
        return None

    try:
        with open(path_file, "r", encoding="utf-8") as f:
            instance_path = f.read().strip()
    except Exception as e:
        logger.error(f"Failed to read {path_file}: {e}")
        return None

    if not instance_path:
        logger.error(f"Instance path is empty in {path_file}")
        return None

    instance_path = Path(instance_path.rstrip("\n"))
    return instance_path


def get_launcher_exe(launch_exe: Path) -> Path:
    """
    Returns the path to the game's launcher executable based on the path file.

    Parameters:
    -----------
    launch_exe : Path
        Path to the launcher executable

    Returns:
    --------
    Path
        Path to the launcher executable, or None if the launcher path is not a file
    """
    return launch_exe.with_name("_" + launch_exe.name) if launch_exe.is_file() else None


def main(argv: list[str]) -> int:
    """
    Main function for the Steam Redirector.

    Parameters:
    -----------
    argv : list[str]
        List of command-line arguments passed to the MO2 instance

    Returns:
    --------
    int
        Exit status code
    """
    add_loggers()
    exit_status = 1
    arg = argv[1] if len(argv) > 1 else None
    if os.getenv("MO2-LINT_NO_REDIRECT") is None:
        os.environ["MO2-LINT_NO_REDIRECT"] = "1"
        exe_path = get_instance_path(instance_path_file)
    else:
        exe_path = get_launcher_exe(Path(argv[0]))

    if not exe_path or exe_path is None:
        logger.error("Failed to determine executable path")
        return exit_status
    elif not exe_path.is_file():
        logger.error(f"Executable not found: {exe_path}")
        return exit_status

    executable = can_execute(exe_path)
    if not executable:
        error = os.strerror(getattr(os, "errno", 0)) if hasattr(os, "errno") else -1
        logger.error(f"File is not executable: {exe_path} (Error: {error})")
        return exit_status

    logger.info(f"Executing: {exe_path} with args: {arg}")
    exit_status = execute(exe_path, [arg] if arg else [])
    if exit_status == 0:
        logger.info(f"Execution completed successfully: {exe_path}")
        exit_status = 0
    else:
        logger.error(f"Execution failed with exit code {exit_status}: {exe_path}")

    remove_loggers()
    return exit_status


if __name__ == "__main__":
    sys.exit(main(sys.argv))
