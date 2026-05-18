#!/usr/bin/env python3

from pathlib import Path
from typing import Optional
from loguru import logger
from pydantic_core import from_json

config_directories = [
    Path("~/.config/heroic").expanduser(),
    Path("~/.var/app/com.heroicgameslauncher.hgl/config/heroic").expanduser(),
]
release_type = [
    "stable",
    "flatpak",
]

gog_data: dict = {}
epic_data: dict = {}


def get_wine_prefix(game_id: str | int, config_directory: Path) -> Optional[Path]:
    """
    Gets the Wine prefix for a Heroic game from its configuration JSON.

    Parameters
    ----------
    game_id : str | int
        The game ID to look up in the Heroic config.
    config_directory : Path
        The path to the Heroic configuration directory.

    Returns
    -------
    Path
        The Wine prefix path.
    """
    config_json = config_directory / "GamesConfig" / f"{game_id}.json"
    if not config_json.exists():
        logger.error(
            f"Game config JSON not found at {config_json}. Unable to retrieve Wine prefix."
        )
        return None

    with open(config_json, "r", encoding="utf-8") as file:
        data = from_json(file.read())
    wine_prefix = data.get(str(game_id), {}).get("winePrefix", {}) or None

    if not wine_prefix:
        logger.warning(
            f"Wine prefix not found in {config_json}. Unable to retrieve Wine prefix."
        )
        return None
    wine_prefix = Path(wine_prefix)

    if not wine_prefix.exists():
        logger.warning(
            f"Wine prefix path {wine_prefix} does not exist. Unable to retrieve Wine prefix."
        )
        return None

    return wine_prefix


def get_wine_path(game_id: str | int, config_directory: Path) -> Optional[str]:
    """
    Gets the Wine binary path for a Heroic game from its configuration JSON.

    Parameters
    ----------
    game_id : str | int
        The game ID to look up in the Heroic config.
    config_directory : Path
        The path to the Heroic configuration directory.

    Returns
    -------
    Optional[str]
        The Wine binary path, or None if not found.
    """
    config_json = config_directory / "GamesConfig" / f"{game_id}.json"
    if not config_json.exists():
        logger.error(
            f"Game config JSON not found at {config_json}. Unable to retrieve Wine path."
        )
        return None

    failed = False
    wine_path = None
    try:
        with open(config_json, "r", encoding="utf-8") as file:
            data = from_json(file.read())
        wine_path = data.get(str(game_id), {}).get("wineVersion", {}).get("bin") or None
    except Exception:
        logger.exception(f"Failed to parse {config_json} for wine path")
        failed = True

    if failed or not wine_path:
        try:
            global_cfg = config_directory / "config.json"
            if global_cfg.exists():
                with open(global_cfg, "r", encoding="utf-8") as file:
                    data = from_json(file.read())
                wine_path = (
                    data.get("defaultSettings", {}).get("wineVersion", {}).get("bin")
                    or None
                )
            else:
                logger.warning(f"Global config JSON not found at {global_cfg}")
                return None
        except Exception:
            logger.exception(f"Failed to parse {global_cfg} for wine version")
            return None

    if not wine_path:
        logger.warning(
            f"Wine path not found in {config_json} or global config. Unable to retrieve Wine path."
        )
        return None

    logger.debug(f"Found wine path: {wine_path}")
    return wine_path


def get_libraries(
    gog_id: Optional[int], epic_id: Optional[str], config_directory: Path
) -> bool:
    """
    Gets Heroic game library directories from the configuration directory.

    Parameters
    ----------
    gog_id : Optional[int]
        GOG game ID to search for.
    epic_id : Optional[str]
        Epic game ID to search for.
    config_directory : Path
        The path to the Heroic configuration directory.

    Returns
    -------
    bool
        True if at least one valid game library was found, False otherwise.
    """
    gog_available = bool(gog_id)
    epic_available = bool(epic_id)

    logger.info(
        f"Attempting to retrieve Heroic game library paths from config directory: {config_directory}"
    )

    def valid():
        if not gog_available and not epic_available:
            logger.warning(
                f"Neither GOG nor Epic game data could be retrieved from {config_directory}."
            )
            return False
        return True

    if not gog_id:
        logger.trace("GOG ID not provided. Marking GOG as unavailable.")
    else:
        gog_data["game_id"] = gog_id
        gog_data["installed_json"] = config_directory / "gog_store" / "installed.json"

    if not epic_id:
        logger.trace("Epic ID not provided. Marking Epic as unavailable.")
    else:
        epic_data["game_id"] = epic_id
        epic_data["installed_json"] = (
            config_directory / "legendaryConfig" / "legendary" / "installed.json"
        )

    if not valid():
        return False

    if gog_available and not gog_data["installed_json"].exists():
        logger.trace(
            f'GOG installed.json not found at "{gog_data["installed_json"]}". Marking GOG as unavailable.',
        )
        gog_available = False
    if epic_available and not epic_data["installed_json"].exists():
        logger.trace(
            f'Epic installed.json not found at "{epic_data["installed_json"]}". Marking Epic as unavailable.'
        )
        epic_available = False
    if not valid():
        return False

    if gog_available:
        try:
            with open(gog_data["installed_json"], "r", encoding="utf-8") as file:
                json = from_json(file.read()).get("installed", [])
                for item in json:
                    if item.get("appName") == str(gog_data["game_id"]):
                        gog_data["json"] = item
                        break
        except Exception:
            logger.exception(f"Failed to parse {gog_data['installed_json']}")
            gog_available = False

        if gog_available and gog_data.get("json"):
            gog_data["install_path"] = Path(gog_data["json"].get("install_path"))
        else:
            logger.warning(
                f"Game with GOG ID {gog_data.get('game_id', gog_id)} not found in installed games list. Marking GOG as unavailable."
            )
            gog_available = False

        if gog_available and not gog_data.get("install_path"):
            logger.warning(
                f"Unable to extract install_path from {gog_data['installed_json']}. Marking GOG as unavailable."
            )
            gog_available = False

    if epic_available:
        try:
            with open(epic_data["installed_json"], "r", encoding="utf-8") as file:
                json = from_json(file.read()).get(epic_data["game_id"], {})
        except Exception:
            logger.exception(f"Unable to parse {epic_data['installed_json']}")
            epic_available = False

        if epic_available and json:
            epic_data["install_path"] = Path(json.get("install_path"))
        else:
            logger.warning(
                f"Game with Epic ID {epic_data.get('game_id', epic_id)} not found in installed games list. Marking Epic as unavailable."
            )
            epic_available = False

        if epic_available and not epic_data.get("install_path"):
            logger.warning(
                f"Unable to extract install_path from {epic_data['installed_json']}. Marking Epic as unavailable."
            )
            epic_available = False

    if not valid():
        return False

    logger.success(
        f"Successfully retrieved library paths from Heroic config. GOG={gog_data.get('install_path')}, Epic={epic_data.get('install_path')}"
    )
    return True


def get_heroic_data(
    gog_id: Optional[int] = None, epic_id: Optional[str] = None
) -> tuple[
    Optional[str], Optional[str], Optional[str | int], Optional[str], Optional[Path]
]:
    """
    Gets Heroic game data from config directories.

    Parameters
    ----------
    gog_id : Optional[int]
        GOG game ID to search for.
    epic_id : Optional[str]
        Epic game ID to search for.

    Returns
    -------
    tuple[Optional[str], Optional[str], Optional[str | int], Optional[str], Optional[Path]]
        A tuple containing (release_type, launcher, app_id, wine_path, wine_prefix).
        Returns (None, None, None, None, None) if no valid data found.
    """
    global gog_data, epic_data
    gog_data = {}
    epic_data = {}

    launcher: Optional[str] = None
    display: Optional[str] = None
    app_id: Optional[str | int] = None
    wine_path: Optional[str] = None
    wine_prefix: Optional[Path] = None
    release: Optional[str] = None

    logger.info("Attempting to retrieve Heroic game data from config directories.")
    for i, dir in enumerate(config_directories):
        release = release_type[i]
        dir = dir.resolve()
        if dir.exists():
            logger.debug(
                f"Found {release} release located at {dir}. Checking for game data."
            )
            if not get_libraries(gog_id, epic_id, dir):
                logger.warning(
                    f"Could not retrieve valid library paths from {dir}. Skipping this directory."
                )
                continue
            elif gog_data and not epic_data:
                logger.trace(f"Found GOG install: {gog_data.get('install_path')}")
                launcher = "gog"
                display = "GOG"
                app_id = gog_data["game_id"]
                wine_path = get_wine_path(gog_data["game_id"], dir)
                wine_prefix = get_wine_prefix(gog_data["game_id"], dir)
            elif epic_data and not gog_data:
                logger.trace(f"Found Epic install: {epic_data.get('install_path')}")
                launcher = "epic"
                display = "Epic"
                app_id = epic_data["game_id"]
                wine_path = get_wine_path(epic_data["game_id"], dir)
                wine_prefix = get_wine_prefix(epic_data["game_id"], dir)
            elif epic_data and gog_data:
                logger.warning(
                    "Both GOG and Epic installs found. Using Epic by default (functionality for handling multiple installs not yet implemented)."
                )
                launcher = "epic"
                display = "Epic (default, GOG also available)"
                app_id = epic_data["game_id"]
                wine_path = get_wine_path(epic_data["game_id"], dir)
                wine_prefix = get_wine_prefix(epic_data["game_id"], dir)
            else:
                logger.trace(
                    f"No valid game data found in {dir}. Skipping this directory."
                )
                launcher, app_id, wine_path, wine_prefix = None, None, None, None
                continue

            # If some values are present but others are missing, treat as incomplete
            if any(
                v is None for v in (launcher, app_id, wine_path, wine_prefix)
            ) and not all(
                v is None for v in (launcher, app_id, wine_path, wine_prefix)
            ):
                logger.warning(
                    f"Received incomplete game data from {dir}. Skipping this directory."
                )
                continue
            else:
                break
        else:
            logger.trace(
                f"Unable to find Heroic config at {dir}. Skipping this directory."
            )
            continue

    if launcher and app_id and wine_path and wine_prefix:
        logger.success(
            f"Successfully retrieved game data for {display} from Heroic config. release={release}, launcher={launcher}, app_id={app_id}, wine_path={wine_path}, wine_prefix={wine_prefix}"
        )
    else:
        logger.warning(
            "Unable to retrieve complete Heroic game data from any config directory."
        )
        release = None

    return release, launcher, app_id, wine_path, wine_prefix
