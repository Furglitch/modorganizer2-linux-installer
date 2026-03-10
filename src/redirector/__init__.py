#!/usr/bin/env python3

from pathlib import Path
from loguru import logger
from logger import add_loggers, remove_loggers
import os
import sys
import json

state_file_path: Path = Path("~/.config/mo2-lint/state.json").expanduser()


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


def get_instance_path(game_dir: Path) -> Path:
    """
    Reads the instance path from the state.json file by matching the game directory.

    Parameters:
    -----------
    game_dir : Path
        The game directory where the redirector is being run from

    Returns:
    --------
    Path
        The instance path for ModOrganizer.exe, or None if an error occurred
    """

    if not state_file_path.is_file():
        logger.error(f"State file not found: {state_file_path}")
        return None

    try:
        with open(state_file_path, "r", encoding="utf-8") as f:
            state_data = json.load(f)
    except Exception as e:
        logger.error(f"Failed to read state file {state_file_path}: {e}")
        return None

    instances = state_data.get("instances", [])
    if not instances:
        logger.error("No instances found in state file")
        return None

    # Normalize the game directory path for comparison
    game_dir_resolved = game_dir.resolve()

    # Find the instance that matches this game directory
    matched_instance = None
    for instance in instances:
        game_path = Path(instance.get("game_path", ""))
        if not game_path:
            continue

        # Check if game_dir is the same as or a child of game_path
        try:
            game_path_resolved = game_path.resolve()
            if (
                game_dir_resolved == game_path_resolved
                or game_path_resolved in game_dir_resolved.parents
            ):
                matched_instance = instance
                break
        except Exception:
            continue

    if not matched_instance:
        logger.error(f"No instance found for game directory: {game_dir}")
        return None

    instance_path = Path(matched_instance.get("instance_path", ""))
    if not instance_path:
        logger.error("Instance path is empty in state file")
        return None

    mo2_exe = instance_path / "ModOrganizer.exe"
    return mo2_exe


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

    # Get the current working directory (game directory)
    game_dir = Path.cwd()
    logger.debug(f"Redirector running from: {game_dir}")

    exe_path = get_instance_path(game_dir)

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
