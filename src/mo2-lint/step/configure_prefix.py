#!/usr/bin/env python3

from loguru import logger
from pathlib import Path
from step.load_game_info import get_launcher
from util import lang, variables as var, state_file as state
from util.heroic.find_library import get_data as get_heroic_data
from util.wine import protontricks, winetricks

default_tricks = [
    "arial",
    "fontsmooth=rgb",
]

yes = ("", "y", "yes")


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


def configure():
    """
    Run the necessary winetricks/protontricks for the selected game launcher.
    """
    tricks = default_tricks + list(var.game_info.tricks)
    logger.debug(f"Configuring prefix with the following tricks: {tricks}")
    match var.launcher:
        case "steam":
            protontricks.apply(var.game_info.launcher_ids.steam, tricks)
        case "gog" | "epic":
            prefix = var.prefix
            winetricks.apply(prefix=prefix, tricks=tricks)


def prompt():
    """
    Prompts the user to confirm their prefix is set up, then configures it.
    """
    prefix = load_prefix()
    for suffix in ["users", "drive_c", "pfx"]:
        if prefix.name == suffix:
            prefix = prefix.parent
    var.prefix = prefix
    logger.trace(f"Resolved prefix path for prompting: {prefix}")

    if not lang.prompt_prefix_init():
        logger.warning(
            "User did not confirm prefix setup. No support will be provided if errors occur."
        )

    configure()
