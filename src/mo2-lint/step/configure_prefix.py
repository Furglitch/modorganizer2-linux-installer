#!/usr/bin/env python3

from datetime import datetime
from loguru import logger
from pathlib import Path
from shutil import copytree, move
from util import variables as var
from util.heroic.find_library import get_data as get_heroic_data
from util.wine import protontricks, winetricks

prompt_archive = """It is highly recommended to clean your current game prefix before starting the installation process.

If you archive your existing prefix, it will be renamed with a timestamp suffix (e.g. '.20240615-123456').
Your personal data (e.g. saved games) will be preserved and restored to the new prefix after it is created.
"""

prompt_archive_done = """Your prefix has been archived and can be found at: {directory}

Personal data from the archived prefix (e.g. saved games) has been preserved and restored to the new prefix.
Feel free to delete the archive if you no longer need it after confirming your data is intact.

A list of all archived prefixes can be found at: TBD"""

prompt_clean_steam = """In order to create a clean game prefix, follow the instructions below:

1. In Steam: right-click the game in your library, select 'Properties', and navigate to the 'Compatibility' tab.
2. Check the box for 'Force the use of a specific Steam Play compatibility tool' if it's not already checked.
3. From the dropdown menu, select your preferred Proton version. 10.0 is the supported and recommended version.
4. Close the properties window and launch the game once to allow Steam to set up the new prefix.
5. Exit the game completely. Do not launch it until the installation process is finished.
"""

prompt_clean_heroic = """In order to create a clean game prefix, follow the instructions below:

1. In Heroic: right-click the game in your library, select 'Settings', and navigate to the 'WINE' tab.
2. Under 'Wine Version', select your preferred Wine/Proton version.
   * Proton - Proton 10.0 is the currently supported and recommended version.
   * If this version is not available, you will need to enable "Allow using Valve Proton builds to run games"
     in Heroic's Settings, under the 'Advanced' tab. Ensure that Proton 10.0 is then downloaded and installed in Steam.
3. Optional: Navigate to the 'OTHER' tab and check 'Use Steam Runtime'. This is recommended and may help with compatibility.
4. Launch the game once to allow Heroic to set up the new prefix.
5. Exit the game completely. Do not launch it until the installation process is finished.
"""

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
    match var.launcher:
        case "steam":
            logger.debug("Loading Steam prefix...")
            prefix = protontricks.get_prefix(var.game_info.launcher_ids.steam)
            logger.trace(f"Loaded Steam prefix: {prefix}")
        case "gog" | "epic":
            logger.debug("Loading Heroic prefix...")
            prefix = get_heroic_data()[3]
            logger.trace(f"Loaded Heroic prefix: {prefix}")
        case _:
            logger.error(f"Unknown launcher: {var.launcher}")

    if prefix is None:
        logger.error("Could not determine game prefix path.")
    elif isinstance(prefix, str):
        prefix = Path(prefix).expanduser()
    elif isinstance(prefix, Path):
        prefix = prefix.expanduser()
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
    match var.launcher:
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
    print(prompt_archive)
    if (
        input(
            "Would you like to archive your current game prefix and create a new one? [y/N]: "
        )
        .strip()
        .lower()
        in yes
    ):
        logger.debug("User agreed to archive the prefix.")
        archive_prefix(prefix)
    else:
        var.archived_prefix = None
        logger.debug("User refused to archive the prefix.")

    # Prompt user to create a clean prefix
    logger.debug("Prompting user to create a clean Steam prefix...")
    match var.launcher:
        case "steam":
            print(prompt_clean_steam)
        case "gog" | "epic":
            print(prompt_clean_heroic)

    if (
        input("Have you completed these instructions? [y/N]: ").strip().lower()
        not in yes
    ):
        logger.critical(
            "User declined to create a clean prefix. Aborting installation."
        )
        raise SystemExit(1)
    else:
        logger.debug("User confirmed clean prefix setup.")
        if var.archived_prefix is not None:
            restore_archived_prefix(prefix)
            print(prompt_archive_done.format(directory=var.archived_prefix))


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
            prefix = var.heroic_config[3]
            winetricks.apply(prefix=prefix, tricks=tricks)
