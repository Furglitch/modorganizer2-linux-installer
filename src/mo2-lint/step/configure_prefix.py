#!/usr/bin/env python3

from datetime import datetime
from loguru import logger
from pathlib import Path
from shutil import copytree, move
from step.load_game_info import get_launcher
from util import lang, variables as var, state_file as state
from util.heroic.find_library import get_data as get_heroic_data
from util.wine import protontricks, winetricks

default_tricks = [
    "arial",
    "fontsmooth=rgb",
]

yes = ("", "y", "yes")

current_time = datetime.now().strftime("%Y%m%d-%H%M%S")


def load_prefix() -> Path:
    """
    Determines the game's wine prefix, based on the relevant launcher.

    Returns
    -------
    Path
        The path to the game's wine prefix.
    """
    logger.debug("Loading game prefix path...")
    prefix = None
    launcher = (
        get_launcher()
        if not state.current_instance
        else state.current_instance.launcher
    )
    match launcher:
        case "steam":
            logger.debug("Loading Steam prefix...")
            prefix = protontricks.get_prefix(var.game_info.launcher_ids.steam)
            logger.trace(f"Loaded Steam prefix: {prefix}")
        case "gog":
            data = get_heroic_data()
            logger.debug("Loading GOG prefix...")
            prefix = data[3]
            if isinstance(prefix, dict):
                prefix = prefix.get("gog")
            logger.trace(f"Loaded GOG prefix: {prefix}")
        case "epic":
            data = get_heroic_data()
            logger.debug("Loading Epic Games prefix...")
            prefix = data[3]
            if isinstance(prefix, dict):
                prefix = prefix.get("epic")
            logger.trace(f"Loaded Epic Games prefix: {prefix}")
        case _:
            logger.error(f"Unknown launcher: {launcher}")

    if prefix is None:
        logger.error("Could not determine game prefix path.")
    elif isinstance(prefix, str):
        prefix = Path(prefix).expanduser().resolve()
    elif isinstance(prefix, Path):
        prefix = prefix.expanduser().resolve()
    var.prefix = prefix
    return prefix


def archive_prefix(prefix: Path):
    """
    Archives the existing game prefix by renaming it with a timestamp suffix.\n
    Sets the global 'archive' variable to the new archive path.

    Parameters
    ----------
    prefix : Path
        Path to the existing game prefix to be archived.
    """
    if prefix.exists() and prefix.is_dir():
        archive_path = prefix.with_suffix(f".{current_time}").expanduser()
        move(prefix, archive_path)
        logger.debug(f"Archived prefix from {prefix} to {archive_path}.")
        var.archived_prefix = archive_path


def restore_archived_prefix(prefix: Path):
    """
    Restores the `users` directory from the archived prefix to the new prefix,\n
    preserving personal data such as saved games.

    Parameters
    ----------
    prefix : Path
        Path to the new game prefix where personal data will be restored.
    """
    match state.current_instance.launcher:
        case "steam":
            subpath = Path("pfx") / "drive_c" / "users"
            src = var.archived_prefix / subpath
        case "gog" | "epic" | _:
            subpath = Path("drive_c") / "users"
            src = var.archived_prefix / subpath
    dst = prefix / subpath
    logger.debug(f"Restoring personal data from {src} to {dst}...")

    copytree(src, dst.with_suffix(".bak"))
    logger.debug(f"Backed up current data at {dst.with_suffix('.bak')}.")
    copytree(src, dst.with_suffix(".old"))
    move(dst.with_suffix(".old"), dst)
    logger.debug(f"Restored personal data to new prefix at {dst}.")


def prompt():
    """
    Prompts the user to archive their existing game prefix and create a clean one.

    Raises
    ------
    SystemExit
        If the user declines to create a clean prefix.
    """

    # Prompt user to archive prefix
    prefix = load_prefix()
    for suffix in ["users", "drive_c", "pfx"]:
        if prefix.name == suffix:
            prefix = prefix.parent
    var.prefix = prefix
    logger.debug(f"Determined game prefix for archiving: {prefix}")
    logger.debug("Prompting user to archive existing prefix...")
    if lang.prompt_archive():
        logger.debug("User agreed to archive the prefix.")
        archive_prefix(prefix)
    else:
        var.archived_prefix = None
        logger.debug("User refused to archive the prefix.")

    # Prompt user to create a clean prefix
    logger.debug("Prompting user to create a clean Steam prefix...")

    if not lang.prompt_archive_init():
        logger.critical(
            "User declined to create a clean prefix. Aborting installation."
        )
        raise SystemExit(1)
    else:
        logger.debug("User confirmed clean prefix setup.")
        if var.archived_prefix is not None:
            restore_archived_prefix(prefix)
            print(lang.prompt_archive_done.format(directory=var.archived_prefix))


def configure():
    """
    Run the necessary winetricks/protontricks for the selected game launcher.
    """
    tricks = default_tricks + list(var.game_info.tricks)
    logger.debug(f"Applying the following tricks: {tricks}")
    match var.launcher:
        case "steam":
            protontricks.apply(var.game_info.launcher_ids.steam, tricks)
        case "gog" | "epic":
            prefix = var.prefix
            winetricks.apply(prefix=prefix, tricks=tricks)
