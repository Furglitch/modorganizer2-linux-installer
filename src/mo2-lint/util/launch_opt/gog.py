#!/usr/bin/env python3


import json
import subprocess
import time
from loguru import logger
from pathlib import Path
from pydantic_core import from_json
from shutil import copy2
from shared.logger import persist_timestamp


def backup_json(json_path: Path) -> Path:
    """
    Backup the goggame-*.info file by creating a copy with a timestamped filename.

    Parameters:
    -----------
    json_path : Path
        The path to the goggame-*.info file to be backed up.

    Returns:
    --------
    Path
        The path to the created backup file.
    """
    timestamp = persist_timestamp()
    backup_path = json_path.with_suffix(f".info.{timestamp}.bak")
    copy2(json_path, backup_path)
    logger.info(f"Backed up {json_path} to {backup_path}")
    return backup_path


def find_gog_info_file(game_path: Path, game_id: str) -> Path | None:
    """
    Find the goggame-*.info file for a specific game.

    Parameters:
    -----------
    game_path : Path
        The root directory of the game installation.
    game_id : str
        The GOG game ID.

    Returns:
    --------
    Path | None
        The path to the goggame-*.info file, or None if not found.
    """
    # Try the exact game ID first
    info_file = game_path / f"goggame-{game_id}.info"
    if info_file.exists():
        return info_file

    # Search for any goggame-*.info file in the directory
    info_files = list(game_path.glob("goggame-*.info"))
    if len(info_files) == 1:
        logger.debug(f"Found GOG info file: {info_files[0]}")
        return info_files[0]
    elif len(info_files) > 1:
        logger.warning(
            f"Multiple goggame-*.info files found in {game_path}. Using first match."
        )
        return info_files[0]

    return None


def read_internal(
    info_path: Path = None,
    game_path: Path = None,
    game_id: str = None,
    output: bool = False,
) -> list[dict]:
    """
    Read the playTasks for a specific GOG game from the goggame-*.info file.

    Parameters:
    -----------
    info_path : Path
        Direct path to the goggame-*.info file. If None, will search using game_path and game_id.
    game_path : Path
        The root directory of the game installation.
    game_id : str
        The GOG game ID.
    output : bool
        Whether to print the playTasks to stdout.

    Returns:
    --------
    list[dict]
        A list of playTask dictionaries for the specified GOG game.
    """
    if info_path is None:
        if game_path is None or game_id is None:
            logger.critical(
                "Either info_path or both game_path and game_id must be provided"
            )
            raise SystemExit(1)
        info_path = find_gog_info_file(game_path, game_id)

    if info_path is None or not info_path.exists():
        logger.critical(f"GOG info file not found at {info_path}")
        raise SystemExit(1)

    with open(info_path, "r", encoding="utf-8") as file:
        data = from_json(file.read())

    play_tasks = data.get("playTasks", [])

    if output:
        game_name = data.get("name", "Unknown Game")
        print(f"Play tasks for {game_name} (GOG ID: {data.get('gameId', 'unknown')}):")
        if not play_tasks:
            print("  No play tasks found")
        else:
            for i, task in enumerate(play_tasks):
                print("-" * 64)
                print(f"Index: {i}")
                print(f"  Name: {task.get('name', '(none)')}")
                print(f"  Type: {task.get('type', '(none)')}")
                print(f"  Path: {task.get('path', '(none)')}")
                print(f"  Category: {task.get('category', '(none)')}")
                print(f"  Arguments: {task.get('arguments', '(none)')}")
                print(f"  Is Primary: {task.get('isPrimary', False)}")
                print(f"  Is Hidden: {task.get('isHidden', False)}")
                print()
    else:
        logger.trace(f"Play tasks for GOG game: {play_tasks}")

    return play_tasks


def add_internal(
    info_path: Path = None,
    game_path: Path = None,
    game_id: str = None,
    executable: str = None,
    arguments: str = None,
    label: str = "Launch Mod Organizer",
    is_primary: bool = False,
    is_hidden: bool = False,
    category: str = "game",
    no_backup: bool = False,
) -> bool:
    """
    Add a playTask for a specific GOG game to the goggame-*.info file.

    Parameters:
    -----------
    info_path : Path
        Direct path to the goggame-*.info file. If None, will search using game_path and game_id.
    game_path : Path
        The root directory of the game installation.
    game_id : str
        The GOG game ID.
    executable : str
        The executable to launch (relative path from game root).
    arguments : str
        Arguments to pass to the executable.
    label : str
        The display name for the playTask.
    is_primary : bool
        Whether this is the primary launch option.
    is_hidden : bool
        Whether this task should be hidden from the user.
    category : str
        The category of the task (e.g., 'game', 'launcher', 'tool', 'document').
    no_backup : bool
        Whether to skip creating a backup of the info file.

    Returns:
    --------
    bool
        True if the playTask was added successfully, False otherwise.
    """
    if info_path is None:
        if game_path is None or game_id is None:
            logger.critical(
                "Either info_path or both game_path and game_id must be provided"
            )
            raise SystemExit(1)
        info_path = find_gog_info_file(game_path, game_id)

    if info_path is None or not info_path.exists():
        logger.critical(f"GOG info file not found at {info_path}")
        raise SystemExit(1)

    with open(info_path, "r", encoding="utf-8") as file:
        data = from_json(file.read())

    play_tasks = data.get("playTasks", [])

    # Check if a playTask with this name already exists
    for task in play_tasks:
        if task.get("name") == label:
            logger.warning(f"PlayTask with name '{label}' already exists for GOG game")
            logger.info("Skipping addition of duplicate playTask")
            return False

    # Create the new playTask
    new_task = {
        "category": category,
        "name": label,
        "path": executable,
        "type": "FileTask",
        "languages": ["*"],
    }

    # Add optional fields
    if arguments:
        new_task["arguments"] = arguments
    if is_primary:
        new_task["isPrimary"] = True
    if is_hidden:
        new_task["isHidden"] = True

    play_tasks.append(new_task)
    data["playTasks"] = play_tasks

    backup = backup_json(info_path) if not no_backup else None
    logger.info(f"Backup created at {backup}" if backup else "No backup created")

    logger.info(f"Adding playTask to GOG game at {info_path}")
    logger.debug(f"  Name: {label}")
    logger.debug(f"  Path: {executable}")
    logger.debug(f"  Arguments: {arguments or '(none)'}")
    logger.debug(f"  Category: {category}")

    with open(info_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

    logger.success("Successfully added playTask for GOG game")
    restart_heroic()
    return True


def remove_internal(
    info_path: Path = None,
    game_path: Path = None,
    game_id: str = None,
    label: str = "Launch Mod Organizer",
    no_backup: bool = False,
) -> bool:
    """
    Remove a playTask for a specific GOG game from the goggame-*.info file.

    Parameters:
    -----------
    info_path : Path
        Direct path to the goggame-*.info file. If None, will search using game_path and game_id.
    game_path : Path
        The root directory of the game installation.
    game_id : str
        The GOG game ID.
    label : str
        The display name of the playTask to remove.
    no_backup : bool, optional
        Whether to skip creating a backup of the info file. Defaults to False.

    Returns:
    --------
    bool
        True if the playTask was removed successfully, False otherwise.
    """
    if info_path is None:
        if game_path is None or game_id is None:
            logger.critical(
                "Either info_path or both game_path and game_id must be provided"
            )
            raise SystemExit(1)
        info_path = find_gog_info_file(game_path, game_id)

    if info_path is None or not info_path.exists():
        logger.critical(f"GOG info file not found at {info_path}")
        raise SystemExit(1)

    with open(info_path, "r", encoding="utf-8") as file:
        data = from_json(file.read())

    play_tasks = data.get("playTasks", [])

    original_length = len(play_tasks)
    play_tasks = [task for task in play_tasks if task.get("name") != label]

    if len(play_tasks) == original_length:
        logger.error(f"PlayTask with name '{label}' not found for GOG game")
        return False

    data["playTasks"] = play_tasks

    backup = backup_json(info_path) if not no_backup else None
    logger.info(f"Backup created at {backup}" if backup else "No backup created")

    logger.info(f"Removing playTask '{label}' from GOG game at {info_path}")

    # Write back to file
    with open(info_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

    logger.success("Successfully removed playTask for GOG game")
    restart_heroic()
    return True


def restart_heroic():
    """
    Restart Heroic Games Launcher by sending a SIGTERM signal to its process.
    """
    try:
        result = subprocess.run(
            ["pgrep", "-x", "heroic"],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
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
