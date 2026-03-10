#!/usr/bin/env python3


import time

from loguru import logger
from pathlib import Path
from pydantic_core import from_json
from shutil import copy2
from shared.logger import persist_timestamp
import json
import subprocess


heroic_config_path = Path(
    "~/.config/heroic/store_cache/legendary_install_info.json"
).expanduser()


def backup_json(json_path: Path) -> Path:
    """
    Backup the legendary_install_info.json file by creating a copy with a timestamped filename.

    Parameters:
    -----------
    json_path : Path
        The path to the legendary_install_info.json file to be backed up.

    Returns:
    --------
    Path
        The path to the created backup file.
    """
    timestamp = persist_timestamp()
    backup_path = json_path.with_suffix(f".json.{timestamp}.bak")
    copy2(json_path, backup_path)
    logger.info(f"Backed up {json_path} to {backup_path}")
    return backup_path


def read_internal(
    json_path: Path = None, epic_id: str = None, output: bool = False
) -> list[dict]:
    """
    Read the launch options for a specific Epic game ID from the legendary_install_info.json file.

    Parameters:
    -----------
    json_path : Path
        The path to the legendary_install_info.json file. If None, will search for it.
    epic_id : str
        The Epic game ID for which to read the launch options.
    output : bool
        Whether to print the launch options to stdout.

    Returns:
    --------
    list[dict]
        A list of launch option dictionaries for the specified Epic game ID.
    """
    if json_path is None:
        json_path = heroic_config_path

    if json_path is None or not json_path.exists():
        logger.critical(f"legendary_install_info.json not found at {json_path}")
        raise SystemExit(1)

    with open(json_path, "r", encoding="utf-8") as file:
        data = from_json(file.read())

    game_data = data.get(epic_id)
    if not game_data:
        logger.critical(f"Epic ID {epic_id} not found in {json_path}")
        raise SystemExit(1)

    game_info = game_data.get("game", {})
    launch_options = game_info.get("launch_options", [])

    if output:
        print(f"Launch options for Epic ID {epic_id}:")
        if not launch_options:
            print("  No launch options found")
        else:
            for i, opt in enumerate(launch_options):
                print("-" * 64)
                print(f"Index: {i}")
                print(f"  Name: {opt.get('name', '(none)')}")
                print(f"  Parameters: {opt.get('parameters', '(none)')}")
                print()
    else:
        logger.trace(f"Launch options for Epic ID {epic_id}: {launch_options}")

    return launch_options


def add_internal(
    json_path: Path = None,
    epic_id: str = None,
    executable: str = None,
    arguments: list = [],
    label: str = "Launch Mod Organizer",
    no_backup: bool = False,
) -> bool:
    """
    Add a launch option for a specific Epic game ID to the legendary_install_info.json file.

    Parameters:
    -----------
    json_path : Path
        The path to the legendary_install_info.json file. If None, will search for it.
    epic_id : str
        The Epic game ID for which to add the launch option.
    executable : str
        The executable to launch.
    arguments : list
        Arguments to pass to the executable.
    label : str
        The display name for the launch option.
    no_backup : bool
        Whether to skip creating a backup of the JSON file.

    Returns:
    --------
    bool
        True if the launch option was added successfully, False otherwise.
    """
    if json_path is None:
        json_path = heroic_config_path

    if json_path is None or not json_path.exists():
        logger.critical(f"legendary_install_info.json not found at {json_path}")
        raise SystemExit(1)

    with open(json_path, "r", encoding="utf-8") as file:
        data = from_json(file.read())

    game_data = data.get(epic_id)
    if not game_data:
        logger.critical(f"Epic ID {epic_id} not found in {json_path}")
        raise SystemExit(1)

    game_info = game_data.get("game", {})
    launch_options = game_info.get("launch_options", [])

    # Check if a launch option with this name already exists
    for opt in launch_options:
        if opt.get("name") == label:
            logger.warning(
                f"Launch option with name '{label}' already exists for Epic ID {epic_id}"
            )
            logger.info("Skipping addition of duplicate launch option")
            return False

    params = f"--override-exe {executable}"
    if arguments:
        params += " " + " ".join(arguments)

    new_option = {"name": label, "parameters": params}

    launch_options.append(new_option)
    game_info["launch_options"] = launch_options

    backup = backup_json(json_path) if not no_backup else None
    logger.info(f"Backup created at {backup}" if backup else "No backup created")

    logger.info(f"Adding launch option to Epic ID {epic_id}")
    logger.debug(f"  Name: {label}")
    logger.debug(f"  Parameters: {params}")

    with open(json_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent="\t")

    logger.success(f"Successfully added launch option for Epic ID {epic_id}")
    return True


def remove_internal(
    json_path: Path = None,
    epic_id: str = None,
    label: str = "Launch Mod Organizer",
    no_backup: bool = False,
) -> bool:
    """
    Remove a launch option for a specific Epic game ID from the legendary_install_info.json file.

    Parameters:
    -----------
    json_path : Path
        The path to the legendary_install_info.json file. If None, defaults to the heroic_config_path.
    epic_id : str
        The Epic game ID for which to remove the launch option.
    label : str
        The display name of the launch option to remove.
    no_backup : bool, optional
        Whether to skip creating a backup of the JSON file. Defaults to False.

    Returns:
    --------
    bool
        True if the launch option was removed successfully, False otherwise.
    """
    if json_path is None:
        json_path = heroic_config_path

    if json_path is None or not json_path.exists():
        logger.critical(f"legendary_install_info.json not found at {json_path}")
        raise SystemExit(1)

    with open(json_path, "r", encoding="utf-8") as file:
        data = from_json(file.read())

    game_data = data.get(epic_id)
    if not game_data:
        logger.critical(f"Epic ID {epic_id} not found in {json_path}")
        raise SystemExit(1)

    game_info = game_data.get("game", {})
    launch_options = game_info.get("launch_options", [])

    original_length = len(launch_options)
    launch_options = [opt for opt in launch_options if opt.get("name") != label]

    if len(launch_options) == original_length:
        logger.error(
            f"Launch option with name '{label}' not found for Epic ID {epic_id}"
        )
        return False

    game_info["launch_options"] = launch_options

    backup = backup_json(json_path) if not no_backup else None
    logger.info(f"Backup created at {backup}" if backup else "No backup created")

    logger.info(f"Removing launch option '{label}' from Epic ID {epic_id}")

    # Write back to file
    with open(json_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent="\t")

    logger.success(f"Successfully removed launch option for Epic ID {epic_id}")
    return True


def restart_epic():
    """
    Restart the Epic Games Launcher by sending a SIGTERM signal to its process.
    """
    try:
        if (
            subprocess.run(
                ["pgrep", "-x", "heroic"],
                capture_output=True,
                text=True,
                check=True,
            )
            != 0
        ):
            logger.debug("Heroic is not running, no restart needed")
            return
        logger.info("Restarting Heroic to apply launch option changes...")
        subprocess.run(["pkill", "-x", "heroic"], check=True)
        time.sleep(5)  # Wait for the process to terminate
        subprocess.Popen(
            ["heroic"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except Exception as e:
        logger.exception(f"Failed to restart Heroic: {e}")
        logger.warning(
            "You may need to manually restart Heroic for changes to take effect."
        )
