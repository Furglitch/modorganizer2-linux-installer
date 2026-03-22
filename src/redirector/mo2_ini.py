#!/usr/bin/env python3
"""Simplified ModOrganizer.ini configuration management."""

from pathlib import Path
from loguru import logger
import configparser


def normalize_path(path: str | Path) -> str:
    """
    Convert a path to Wine-style Z:\\ Windows path format for INI storage.

    Parameters:
    -----------
    path : str | Path
        Path to convert (POSIX or Windows-style)

    Returns:
    --------
    str
        Windows-style Z:\\ path with escaped backslashes for INI storage
    """
    s = str(path).replace("/", "\\")

    # If already has drive letter, keep it; otherwise add Z:\
    if not (len(s) > 1 and s[1] == ":"):
        s = "Z:\\" + s.lstrip("\\")

    return s.replace("\\", "\\\\")  # Escape for INI


def update_mo2_ini(
    mo2_instance_path: Path, game_executable: str, launcher_args: list[str]
) -> bool:
    """
    Update ModOrganizer.ini with launcher arguments for the game executable.

    Creates or updates the customExecutables section to include launcher arguments
    that games need (like Epic auth tokens). If the INI doesn't exist, creates it.

    Parameters:
    -----------
    mo2_instance_path : Path
        Path to the MO2 instance directory
    game_executable : str
        Full path to the game executable
    launcher_args : list[str]
        List of arguments from the launcher to pass to the game

    Returns:
    --------
    bool
        True if successful, False otherwise
    """
    ini_path = mo2_instance_path / "ModOrganizer.ini"
    args_string = " ".join(launcher_args)

    logger.debug(f"Updating {ini_path} with args: {args_string}")

    config = configparser.RawConfigParser()
    config.optionxform = str  # Preserve case

    if ini_path.exists():
        try:
            config.read(ini_path, encoding="utf-8")
        except Exception as e:
            logger.warning(f"Failed to read existing INI: {e}")

    if "customExecutables" not in config:
        config.add_section("customExecutables")
        config.set("customExecutables", "size", "0")

    section = config["customExecutables"]
    size = int(section.get("size", 0))

    # Find matching executable by filename
    game_name = Path(game_executable).name
    updated = False

    for i in range(1, size + 1):
        binary = section.get(f"{i}\\binary", "")
        if Path(binary.replace("\\\\", "\\")).name.lower() == game_name.lower():
            logger.info(f"Updating existing executable #{i}")
            section[f"{i}\\arguments"] = args_string
            section[f"{i}\\binary"] = normalize_path(game_executable)
            updated = True
            break

    # If not found, add new entry
    if not updated:
        new_idx = size + 1
        logger.info(f"Adding new executable entry #{new_idx}")
        section[f"{new_idx}\\arguments"] = args_string
        section[f"{new_idx}\\binary"] = normalize_path(game_executable)
        section[f"{new_idx}\\title"] = Path(game_executable).stem
        section[f"{new_idx}\\toolbar"] = "false"
        section[f"{new_idx}\\ownicon"] = "true"
        section[f"{new_idx}\\hide"] = "false"
        section[f"{new_idx}\\steamAppID"] = ""
        section["size"] = str(new_idx)

    try:
        with open(ini_path, "w", encoding="utf-8") as f:
            config.write(f, space_around_delimiters=False)
        logger.success("Updated ModOrganizer.ini")
        return True
    except Exception as e:
        logger.exception(f"Failed to write INI: {e}")
        return False
