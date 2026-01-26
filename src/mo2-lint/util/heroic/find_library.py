#!/usr/bin/env python3

from loguru import logger
from pathlib import Path

from pydantic_core import from_json
from util.variables import game_info, input

config_directories = [
    Path("~/.config/heroic").expanduser(),
    Path("~/.var/app/com.heroicgameslauncher.hgl/config/heroic").expanduser(),
]
release_type = [
    "stable",
    "flatpak",
]

gog_data = {}
epic_data = {}


def get_data() -> tuple[str, str, str, str, str]:
    """
    Returns
    -------
    tuple[str, str, str, str, str]
        A tuple containing the launcher type, game ID, install path, Wine path, and Wine prefix.
    """
    launcher: str = None
    display: str = None
    game_id: str | int = None
    install_path: Path = None
    wine_path: Path = None
    wine_prefix: Path = None
    for i, dir in enumerate(config_directories):
        release = release_type[i]
        dir = dir.resolve()
        if dir.exists():
            logger.debug(f"Found {release} release. Heroic config located at {dir}")
            if not get_libraries(dir):
                logger.error("No valid Heroic libraries found.")
                continue
            elif gog_data and not epic_data:
                launcher = "gog"
                display = "GOG"
                game_id = gog_data["game_id"]
                install_path = Path(gog_data["install_path"])
                wine_path, wine_prefix = get_wine_variables(gog_data["game_id"], dir)
            elif epic_data and not gog_data:
                launcher = "epic"
                display = "Epic"
                game_id = epic_data["game_id"]
                install_path = Path(epic_data["install_path"])
                wine_path, wine_prefix = get_wine_variables(epic_data["game_id"], dir)
            elif epic_data and gog_data:
                logger.error(
                    "Both GOG and Epic libraries found. Functionality not yet implemented."  # TODO
                )
                launcher, game_id, install_path, wine_path, wine_prefix = (
                    None,
                    None,
                    None,
                    None,
                    None,
                )
            else:
                launcher, game_id, install_path, wine_path, wine_prefix = (
                    None,
                    None,
                    None,
                    None,
                    None,
                )

            if not all(
                v is None
                for v in (install_path, launcher, game_id, wine_path, wine_prefix)
            ):
                logger.warning(
                    f"Incomplete library information detected for {display}."
                )
                continue
            else:
                break
        else:
            logger.warning(f"Unable to find Heroic config at {dir}")

    global heroic_config
    heroic_config = (launcher, game_id, install_path, wine_path, wine_prefix)
    return heroic_config


def get_libraries(config_directory: Path) -> tuple[Path | None, Path | None]:
    """
    Parameters
    ----------
    config_directory : Path
        The path to the Heroic configuration directory.

    Returns
    -------
    tuple[Path | None, Path | None]
        A tuple containing the install paths for Epic and GOG games, or None if not found
    """
    gog_available = True
    epic_available = True

    def valid():
        if not gog_available and not epic_available:
            logger.warning("No valid libraries found.")
            return False
        return True

    if not game_info.get(input.game).launcher_ids.gog:
        gog_available = False
        logger.warning("GOG ID is not set for game.")
    else:
        gog_data["game_id"] = game_info.get(input.game).launcher_ids.gog
        gog_data["installed_json"] = config_directory / "gog_store" / "installed.json"
    if not game_info.get(input.game).launcher_ids.epic:
        epic_available = False
        logger.warning("Epic ID is not set for game.")
    else:
        epic_data["game_id"] = game_info.get(input.game).launcher_ids.epic
        epic_data["installed_json"] = (
            config_directory / "legendaryConfig" / "legendary" / "installed.json"
        )
    if not valid():
        return None

    if gog_available and not gog_data["installed_json"].exists():
        gog_available = False
        logger.warning(f'installed.json not found at "{gog_data["installed_json"]}"')
    if epic_available and not epic_data["installed_json"].exists():
        epic_available = False
        logger.warning(f'installed.json not found at "{epic_data["installed_json"]}"')
    if not valid():
        return None

    while gog_available:
        with open(gog_data["installed_json"], "r", encoding="utf-8") as file:
            gog_data["json"] = from_json(file.read()).get("installed", [])
            for item in gog_data["json"]:
                if item.get("appName") == str(gog_data["game_id"]):
                    gog_data["json"] = item
                    break
        if gog_data["json"]:
            gog_data["install_path"] = Path(gog_data["json"].get("install_path"))
        else:
            logger.warning("Game not found in installed GOG games.")
            gog_available = False
        if not gog_data["install_path"]:
            logger.warning(
                f"Unable to extract install_path from {gog_data['installed_json']}"
            )
            gog_available = False

    while epic_available:
        with open(epic_data["installed_json"], "r", encoding="utf-8") as file:
            epic_data["json"] = from_json(file.read()).get(epic_data["game_id"], {})
        if epic_data["json"]:
            epic_data["install_path"] = Path(epic_data["json"].get("install_path"))
        else:
            logger.warning("Game not found in installed Epic games.")
            epic_available = False
        if not epic_data["install_path"]:
            logger.warning(
                f"Unable to extract install_path from {epic_data['installed_json']}"
            )
            epic_available = False

    if not valid():
        return None
    return epic_data["install_path"], gog_data["install_path"]


def get_wine_variables(
    game_id: str | int, config_directory: Path
) -> tuple[str | None, str | None]:
    """
    Parameters
    ----------
    game_id : str | int
        The game ID to look up in the Heroic config.
    config_directory : Path
        The path to the Heroic configuration directory.

    Returns
    -------
    tuple[str | None, str | None]
        A tuple containing the Wine binary path and Wine prefix, or None if not found.
    """

    config_json = config_directory / "GamesConfig" / f"{game_id}.json"
    if not config_json.exists():
        logger.warning(f'Config JSON not found at "{config_json}"')
    else:
        with open(config_json, "r", encoding="utf-8") as file:
            data = from_json(file.read())
    wine_path = data.get(str(game_id), {}).get("wineVersion", {}).get("bin") or None

    if not wine_path:
        logger.warning(f"Wine path not found in {config_json}, checking global config.")
        config_json = config_directory / "config.json"
        if not config_json.exists():
            logger.warning(f'Global config JSON not found at "{config_json}"')
            return None
        with open(config_json, "r", encoding="utf-8") as file:
            data = from_json(file.read())
            wine_path = (
                data.get("defaultSettings", {}).get("wineVersion", {}).get("bin")
                or None
            )

    if not wine_path:
        logger.warning(f"Wine path not found in both {config_json} and global config.")
        return None
    wine_path = Path(wine_path)

    logger.debug(f"Found wine path: {wine_path}")

    with open(config_json, "r", encoding="utf-8") as file:
        data = from_json(file.read())
    wine_prefix = data.get(str(game_id), {}).get("winePrefix", {}) or None

    if not wine_prefix:
        logger.warning(f"Wine prefix not found in {config_json}.")
        return None
    wine_prefix = Path(wine_prefix)

    return wine_path, wine_prefix
