#!/usr/bin/env python3

from pathlib import Path
from loguru import logger
from shared.logger import add_loggers, remove_loggers
import os
import sys
import json
import yaml

STATE_FILE = Path("~/.config/mo2-lint/state.json").expanduser()


def get_internal_file(relative_path: str) -> Path:
    """
    Gets the path to an internal file. Handles both dev and built environments.

    Parameters:
    -----------
    relative_path : str
        Relative path to the file from the project root

    Returns:
    --------
    Path
        Absolute path to the internal file
    """
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / "cfg" / relative_path
    return Path(__file__).parent.parent.parent / "configs" / relative_path


def load_launcher_prefixes() -> list[str]:
    """
    Loads launcher-specific argument prefixes from the YAML configuration file.

    Returns:
    --------
    list[str]
        Flattened list of all launcher argument prefixes to filter
    """
    try:
        config_path = get_internal_file("arg_pass.yml")
        with open(config_path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        prefixes = []
        for category_prefixes in data.values():
            if isinstance(category_prefixes, list):
                prefixes.extend(category_prefixes)

        logger.debug(f"Loaded {len(prefixes)} launcher argument prefixes")
        return prefixes
    except Exception as e:
        logger.warning(f"Failed to load launcher args config: {e}")
        return []


def get_instance_info(game_dir: Path) -> tuple[Path | None, str | None]:
    """
    Retrieves the ModOrganizer.exe path and game executable from the state file.

    Parameters:
    -----------
    game_dir : Path
        Path to the game installation directory

    Returns:
    --------
    tuple[Path | None, str | None]
        Tuple of (mo2_exe_path, game_executable_path), or (None, None) if an error occurred
    """
    if not STATE_FILE.is_file():
        logger.error(f"State file not found: {STATE_FILE}")
        return None, None

    try:
        with open(STATE_FILE, encoding="utf-8") as f:
            state = json.load(f)
    except Exception as e:
        logger.error(f"Failed to read state file: {e}")
        return None, None

    game_dir_resolved = game_dir.resolve()

    # Find matching instance
    for instance in state.get("instances", []):
        try:
            game_path = Path(instance.get("game_path", "")).resolve()
            if game_dir_resolved == game_path or game_path in game_dir_resolved.parents:
                instance_path = Path(instance["instance_path"])
                game_exe = instance.get("game_executable", "")

                # Build full path to game executable
                if game_exe:
                    game_exe = str((game_path / game_exe).resolve())

                return instance_path / "ModOrganizer.exe", game_exe
        except Exception:
            continue

    logger.error(f"No instance found for: {game_dir}")
    return None, None


def split_arguments(
    args: list[str], prefixes: list[str]
) -> tuple[list[str], list[str]]:
    """
    Separates arguments into launcher-specific and non-launcher arguments.

    Parameters:
    -----------
    args : list[str]
        List of command-line arguments
    prefixes : list[str]
        List of launcher argument prefixes to extract

    Returns:
    --------
    tuple[list[str], list[str]]
        Tuple of (launcher_args, other_args)
    """
    if not prefixes:
        return [], args

    launcher_args = []
    other_args = []

    for arg in args:
        if any(arg.startswith(prefix) for prefix in prefixes):
            launcher_args.append(arg)
            logger.debug(f"Extracted launcher arg: {arg}")
        else:
            other_args.append(arg)

    return launcher_args, other_args


def execute_mo2(exe: Path, args: list[str]) -> int:
    """
    Executes ModOrganizer.exe using Wine with the provided arguments.

    Parameters:
    -----------
    exe : Path
        Path to the ModOrganizer.exe file
    args : list[str]
        List of arguments to pass to the executable

    Returns:
    --------
    int
        Exit status of the executed process
    """
    wine = os.getenv("WINE", "wine64")
    try:
        os.execlp(wine, wine, str(exe), *args)
        return 0
    except Exception as e:
        logger.error(f"Failed to execute {exe}: {e}")
        return 1


def main(argv: list[str]) -> int:
    """
    Main function for the MO2 Redirector.

    Captures launcher-specific arguments (like Epic auth tokens) and writes them to
    ModOrganizer.ini so games launched from MO2 receive the necessary parameters.

    Parameters:
    -----------
    argv : list[str]
        List of command-line arguments passed to the redirector

    Returns:
    --------
    int
        Exit status code
    """
    try:
        add_loggers(script="redirector", process="redirector")
        logger.info("MO2 Redirector started")
        logger.debug(f"Arguments: {argv}")
    except Exception as e:
        print(f"ERROR: Failed to initialize logger: {e}", file=sys.stderr)
        return 1

    try:
        game_dir = Path.cwd()
        logger.debug(f"Running from: {game_dir}")

        # Load launcher argument prefixes and split arguments
        prefixes = load_launcher_prefixes()
        launcher_args, other_args = split_arguments(argv[1:], prefixes)

        # Find MO2 instance for this game
        mo2_exe, game_executable = get_instance_info(game_dir)

        if not mo2_exe:
            logger.error("Failed to find MO2 instance")
            return 1

        if not mo2_exe.is_file():
            logger.error(f"MO2 executable not found: {mo2_exe}")
            return 1

        # Update ModOrganizer.ini with launcher arguments if present
        if launcher_args and game_executable:
            logger.info(f"Updating INI with {len(launcher_args)} launcher arguments")
            try:
                try:
                    from .mo2_ini import update_mo2_ini
                except ImportError:
                    from mo2_ini import update_mo2_ini

                update_mo2_ini(mo2_exe.parent, game_executable, launcher_args)
            except Exception as e:
                logger.warning(f"Failed to update INI: {e}")

        # Execute MO2
        logger.info(
            f"Launching: {mo2_exe}"
            + (f" with args: {other_args}" if other_args else "")
        )
        return execute_mo2(mo2_exe, other_args)

    except Exception as e:
        logger.error(f"Redirector error: {e}")
        logger.exception("Traceback:")
        return 1
    finally:
        remove_loggers()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
