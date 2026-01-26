#!/usr/bin/env python3

from loguru import logger
from pathlib import Path
from datetime import datetime
from util.variables import (
    launcher,
    input,
    game_info,
    heroic_config,
    archived_prefix as archive,
)
from util.wine import protontricks, winetricks
from shutil import copy2, move

prompt_archive = """It is highly recommended to clean your current game prefix before starting the installation process.
"""

prompt_archive_done = """Your prefix has been archived and can be found at: {directory}

Personal data from the archived prefix (e.g. saved games) has been preserved and restored to the new prefix.
Feel free to delete the archive if you no longer need it after confirming your data is intact.

A list of all archived prefixes can be found at: TBD"""

prompt_clean_steam = """In order to create a clean game prefix, follow the instructions below:

1. In Steam: right-click the game in your library, select 'Properties', and navigate to the 'Compatibility' tab.
2. Check the box for 'Force the use of a specific Steam Play compatibility tool' if it's not already checked.
   * Proton 9.0 is the currently supported and recommended version
3. From the dropdown menu, select your preferred Proton version. 9.0 is the supported and recommended version.
4. Close the properties window and launch the game once to allow Steam to set up the new prefix.
5. Exit the game completely. Do not launch it until the installation process is finished.
"""

prompt_clean_heroic = """In order to create a clean game prefix, follow the instructions below:

1. In Heroic: right-click the game in your library, select 'Settings', and navigate to the 'WINE' tab.
2. Under 'Wine Version', select your preferred Wine/Proton version.
   * Proton - Proton 9.0 (Beta) is the currently supported and recommended version.
     This is a stable release, not beta, but Valve never changed the file name.
   * If this version is not available, you will need to enable "Allow using Valve Proton builds to run games"
     in Heroic's Settings, under the 'Advanced' tab. Ensure that Proton 9.0 is then downloaded and installed in Steam.
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


def load_prefix():
    match launcher:
        case "steam":
            prefix = protontricks.get_prefix(
                game_info.get(input.game).launcher_ids.steam
            )
        case "gog" | "epic":
            prefix = heroic_config[4]
    return prefix or None


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
        global archive
        archive = archive_path


def restore_archived_prefix(prefix: Path):
    """
    Restores the `users` directory from the archived prefix to the new prefix,\n
    preserving personal data such as saved games.

    Parameters
    ----------
    prefix : Path
        Path to the new game prefix where personal data will be restored.
    """
    match launcher:
        case "steam":
            src = archive / "pfx" / "drive_c" / "users"
        case "gog" | "epic":
            src = archive / "drive_c" / "users"
    dst = prefix / "drive_c" / "users"

    move(dst, dst.with_suffix(".bak"))
    copy2(src, dst)


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
    print(prompt_archive)
    if (
        input(
            "Would you like to archive your current game prefix and create a new one? [y/N]: "
        )
        .strip()
        .lower()
        in yes
    ):
        archive_prefix(prefix)
        if archive is not None:
            restore_archived_prefix(prefix)
        print(prompt_archive_done.format(directory=archive))

    else:
        logger.debug("User refused to archive the prefix.")

    # Prompt user to create a clean prefix
    match launcher:
        case "steam":
            print(prompt_clean_steam)
        case "gog" | "epic":
            print(prompt_clean_heroic)

    if (
        input("Have you completed these instructions? [y/N]: ").strip().lower()
        not in yes
    ):
        logger.critical("Aborting operation...")
        raise SystemExit(1)
    else:
        logger.debug("User confirmed clean prefix setup.")


def configure():
    """
    Run the necessary winetricks/protontricks for the selected game launcher.
    """
    tricks = default_tricks + game_info.get(input.game).get("protontricks_args", [])
    match launcher:
        case "steam":
            protontricks.apply(game_info.get(input.game).launcher_ids.steam, tricks)
        case "gog" | "epic":
            wine, prefix = heroic_config[3], heroic_config[4]
            if wine.name == "proton":
                wine = wine.parent / "files" / "bin" / "wine"
            winetricks.apply(wine, prefix, tricks)
