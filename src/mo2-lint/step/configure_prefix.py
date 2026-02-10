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

    logger.debug("Loading game prefix based on launcher information.")
    prefix = None
    launcher = (
        get_launcher()
        if not state.current_instance
        else state.current_instance.launcher
    )
    match launcher:
        case "steam":
            logger.trace("Attempting to retrieve Steam prefix using protontricks.")
            prefix = protontricks.get_prefix(var.game_info.launcher_ids.steam)
        case "gog":
            logger.trace("Attempting to retrieve GOG prefix using heroic data.")
            data = get_heroic_data()
            prefix = data[3]
            if isinstance(prefix, dict):
                prefix = prefix.get("gog")
        case "epic":
            logger.trace("Attempting to retrieve Epic prefix using heroic data.")
            data = get_heroic_data()
            prefix = data[3]
            if isinstance(prefix, dict):
                prefix = prefix.get("epic")
        case _:
            logger.critical(
                f"Unrecognized launcher '{launcher}'. Unable to determine prefix path."
            )
            logger.critical(
                "This should not happen. Please report this issue to the developer."
            )
            raise SystemExit(1)

    if prefix is None:
        logger.critical(
            "Failed to determine prefix path from launcher data. Please ensure you've set up your prefix properly and have run the game at least once."
        )
        raise SystemExit(1)
    elif isinstance(prefix, str):
        prefix = Path(prefix).expanduser().resolve()
    elif isinstance(prefix, Path):
        prefix = prefix.expanduser().resolve()
    logger.debug(f"Determined prefix path: {prefix}")
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
        logger.trace(f"Backed up existing prefix from {prefix} to {archive_path}")
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
    logger.trace(
        f"Restoring personal data from archived prefix. Source: {src}, Destination: {dst}"
    )

    copytree(src, dst.with_suffix(".bak"))
    logger.trace(
        f"Copied personal data to temporary backup location: {dst.with_suffix('.bak')}"
    )
    copytree(src, dst.with_suffix(".old"))
    move(dst.with_suffix(".old"), dst)
    logger.trace(
        f"Restored personal data to new prefix at {dst}. Original data backed up at {dst.with_suffix('.bak')}"
    )


def configure():
    """
    Run the necessary winetricks/protontricks for the selected game launcher.
    """
    tricks = default_tricks + list(var.game_info.tricks)
    logger.info(f"Configuring prefix with the following tricks: {tricks}")
    match var.launcher:
        case "steam":
            protontricks.apply(var.game_info.launcher_ids.steam, tricks)
        case "gog" | "epic":
            prefix = var.prefix
            winetricks.apply(prefix=prefix, tricks=tricks)


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
    logger.trace(f"Resolved prefix path for prompting: {prefix}")
    logger.debug(f"Prompting user to archive existing prefix at {prefix}")
    if lang.prompt_archive():
        logger.trace(
            "User agreed to archive existing prefix. Proceeding with archival."
        )
        archive_prefix(prefix)
    else:
        logger.warning(
            "User declined to archive existing prefix. Proceeding without archival."
        )
        var.archived_prefix = None

    # Prompt user to create a clean prefix
    if not lang.prompt_archive_init():
        logger.warning(
            "User declined that instructions were followed to create a clean prefix. No support will be provided if errors occur."
        )

    if var.archived_prefix is not None:
        configure()
        restore_archived_prefix(prefix)
        print(lang.prompt_archive_done.format(directory=var.archived_prefix))
