#!/usr/bin/env python3

from pathlib import Path
from loguru import logger
from shared.logger import add_loggers, remove_loggers
import os
import sys
import json
import yaml
import subprocess

# Running inside Wine/Proton: Z:\ is Linux root, C:\ is prefix
STATE_FILE = (
    Path("Z:/home") / os.environ.get("USER", "user") / ".config/mo2-lint/state.json"
)


def wine_to_posix(wine_path: str | Path) -> Path:
    """
    Convert a Wine (Z:\\) path to POSIX path.

    Parameters:
    -----------
    wine_path : str | Path
        Windows-style path (may use \\ or /)

    Returns:
    --------
    Path
        POSIX path
    """
    path_str = str(wine_path).replace("\\", "/")

    if path_str.upper().startswith("Z:/"):
        return Path(path_str[2:])  # Remove "Z:"

    if path_str.startswith("/"):  # Already a POSIX path
        return Path(path_str)

    return Path(path_str)  # For C:\ or other Windows drives, try to resolve as-is


def posix_to_wine(posix_path: str | Path) -> str:
    """
    Convert a POSIX path to Wine (Z:\\) path.

    Parameters:
    -----------
    posix_path : str | Path
        POSIX filesystem path

    Returns:
    --------
    str
        Windows-style Z:\\ path
    """
    path_str = str(posix_path).replace("\\", "/")

    # Already a Wine path, return as-is with backslashes
    if len(path_str) > 1 and path_str[1] == ":":
        return path_str.replace("/", "\\")

    # Convert POSIX to Wine Z:\ path
    path = Path(posix_path).resolve()
    wine_path = "Z:\\" + str(path).lstrip("/").replace("/", "\\")
    return wine_path


def write_error_log(error_log: Path, message: str, exc: Exception) -> None:
    """
    Write error information to a fallback error log file.

    Parameters:
    -----------
    error_log : Path
        Wine Z:\\ path to the error log file
    message : str
        Error message to write
    exc : Exception
        Exception object for traceback
    """
    try:
        wine_to_posix(error_log.parent).mkdir(parents=True, exist_ok=True)
        with open(wine_to_posix(error_log), "a") as f:
            import traceback

            f.write(f"{message}: {exc}\n")
            f.write(traceback.format_exc())
    except Exception:
        pass  # Nothing we can do if error logging fails


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
        Path to the game installation directory (may be Wine or POSIX path)

    Returns:
    --------
    tuple[Path | None, str | None]
        Tuple of (mo2_exe_path as Wine path, game_executable_path as POSIX str), or (None, None) if an error occurred
    """
    # Try to read state file with Wine path
    state_file_posix = wine_to_posix(STATE_FILE)
    if not state_file_posix.is_file():
        logger.error(f"State file not found: {state_file_posix}")
        return None, None

    try:
        with open(state_file_posix, encoding="utf-8") as f:
            state = json.load(f)
    except Exception as e:
        logger.error(f"Failed to read state file: {e}")
        return None, None

    # Convert Wine path to POSIX for comparison
    game_dir_posix = wine_to_posix(game_dir).resolve()
    logger.trace(f"Game dir (Wine): {game_dir}")
    logger.trace(f"Game dir (POSIX): {game_dir_posix}")

    for instance in state.get("instances", []):
        try:
            # State file stores POSIX paths
            game_path = Path(instance.get("game_path", "")).resolve()
            instance_path = Path(instance["instance_path"]).resolve()

            logger.trace(f"Checking instance game_path: {game_path}")

            # Check if game_dir is at or under game_path
            if game_dir_posix == game_path or game_path in game_dir_posix.parents:
                game_exe = instance.get("game_executable", "")

                # Build full POSIX path to game executable
                if game_exe:
                    game_exe = str((game_path / game_exe).resolve())

                # Return both as Wine Z:\ paths for Wine compatibility
                mo2_exe_wine = posix_to_wine(instance_path / "ModOrganizer.exe")

                logger.debug(f"Found MO2 instance: {mo2_exe_wine}")
                logger.debug(f"Game executable: {game_exe}")

                # Return Wine path string for mo2_exe so subprocess can use it directly
                return Path(mo2_exe_wine), game_exe
        except Exception as e:
            logger.trace(f"Instance check failed: {e}")
            continue

    logger.error(f"No instance found for: {game_dir_posix}")
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
    Executes ModOrganizer.exe directly (already running inside Wine/Proton).

    Parameters:
    -----------
    exe : Path
        Wine-format path to the ModOrganizer.exe file (e.g., Z:\\path\\to\\MO2.exe)
    args : list[str]
        List of arguments to pass to the executable

    Returns:
    --------
    int
        Exit status of the executed process
    """
    exe_str = str(exe)
    logger.debug(f"Executing: {exe_str} {args}")

    try:
        result = subprocess.run([exe_str] + args)
        return result.returncode
    except Exception as e:
        logger.error(f"Failed to execute {exe_str}: {e}")
        return 1


def main(argv: list[str]) -> int:
    """
    Parameters:
    -----------
    argv : list[str]
        List of command-line arguments passed to the redirector

    Returns:
    --------
    int
        Exit status code
    """
    user = os.environ.get("USER", "user")
    log_dir = Path(f"Z:/home/{user}/.cache/mo2-lint/logs")
    error_log = log_dir / "redirector.error.log"

    console_sink = None
    try:
        console_sink = open(os.devnull, "w")
        add_loggers(
            script="redirector",
            process="redirector",
            log_path=log_dir,
            console_sink=console_sink,
            log_level="TRACE",
        )
        logger.info("MO2 Redirector started")
        logger.debug(f"Arguments: {argv}")
    except Exception as e:  # Logger failed, write to error fallback log
        write_error_log(error_log, "Logger init failed", e)
        return 1

    try:
        game_dir = Path.cwd()
        logger.debug(f"Running from: {game_dir}")
        logger.trace(f"Environment USER: {os.environ.get('USER', 'unknown')}")

        # Load launcher argument prefixes and split arguments
        prefixes = load_launcher_prefixes()
        launcher_args, other_args = split_arguments(argv[1:], prefixes)
        # launcher_args = [arg for arg in argv]; other_args = [] # bypass filter

        logger.trace(f"argv: {argv}")
        logger.trace(f"argv[1:]: {argv[1:]}")
        logger.trace(f"Launcher args: {launcher_args}")
        logger.trace(f"Other args: {other_args}")

        # Find MO2 instance for this game
        mo2_exe, game_executable = get_instance_info(game_dir)
        if not mo2_exe:
            logger.error("Failed to find MO2 instance")
            return 1

        # mo2_exe is already a Wine path string, check by trying to convert to POSIX
        mo2_exe_posix = wine_to_posix(mo2_exe)
        if not mo2_exe_posix.is_file():
            logger.error(
                f"MO2 executable not found: {mo2_exe} (POSIX: {mo2_exe_posix})"
            )
            return 1

        # Update ModOrganizer.ini with launcher arguments if present
        if launcher_args and game_executable:
            logger.info(f"Updating INI with {len(launcher_args)} launcher arguments")
            try:
                try:
                    from .mo2_ini import update_mo2_ini
                except ImportError:
                    from mo2_ini import update_mo2_ini

                # mo2_exe is Wine format, convert to POSIX for INI update
                mo2_dir_posix = wine_to_posix(mo2_exe).parent
                update_mo2_ini(mo2_dir_posix, game_executable, launcher_args)
            except Exception as e:
                logger.warning(f"Failed to update INI: {e}")

        logger.info(
            f"Launching: {mo2_exe}"
            + (f" with args: {other_args}" if other_args else "")
        )
        return execute_mo2(mo2_exe, other_args)

    except Exception as e:
        logger.error(f"Redirector error: {e}")
        logger.exception("Traceback:")
        write_error_log(
            error_log, "Redirector error", e
        )  # Also write to error log as backup
        return 1
    finally:
        remove_loggers()
        if console_sink:
            console_sink.close()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
