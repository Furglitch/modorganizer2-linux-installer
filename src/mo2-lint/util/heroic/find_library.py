#!/usr/bin/env python3

from loguru import logger
from pathlib import Path
from pydantic_core import from_json
from util import variables as var

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


def get_data() -> tuple[
    str | dict[str | str],
    str | int | dict[str, str | int],
    Path | dict[str, Path],
    Path | dict[str, Path],
]:
    """
    Gets Heroic game data from config directories.

    Returns
    -------
    tuple[str, str| int, Path, Path]
        A tuple containing the launcher type, game ID, install path, and Wine prefix.

    tuple[dict[str,str], dict[str, str|int], dict[str, Path], dict[str, Path]]
        A tuple containing entries for launcher type, game ID, install path, and Wine prefix
        for both GOG and Epic launchers.
        First str is "gog" or "epic".

    Values are: launcher, game_id, install_path, wine_prefix
    """

    launcher: str = None
    display: str = None
    game_id: str | int = None
    install_path: Path = None
    wine_prefix: Path = None

    logger.info("Attempting to retrieve Heroic game data from config directories.")
    for i, dir in enumerate(config_directories):
        release = release_type[i]
        dir = dir.resolve()
        if dir.exists():
            logger.debug(
                f"Found {release} release located at {dir}. Checking for game data."
            )
            if not get_libraries(dir):
                logger.warning(
                    f"Could not retrieve valid library paths from {dir}. Skipping this directory."
                )
                continue
            elif gog_data and not epic_data:
                logger.trace(f"Found GOG install: {gog_data.get('install_path')}")
                launcher = "gog"
                display = "GOG"
                game_id = gog_data["game_id"]
                install_path = Path(gog_data["install_path"])
                wine_prefix = get_wine_prefix(gog_data["game_id"], dir)
            elif epic_data and not gog_data:
                logger.trace(f"Found Epic install: {epic_data.get('install_path')}")
                launcher = "epic"
                display = "Epic"
                game_id = epic_data["game_id"]
                install_path = Path(epic_data["install_path"])
                wine_prefix = get_wine_prefix(epic_data["game_id"], dir)
            elif epic_data and gog_data:
                logger.trace(
                    f"Found both GOG and Epic installs: {gog_data.get('install_path')}, {epic_data.get('install_path')}"
                )
                launcher: dict[str, str] = {}
                display = "GOG and Epic"
                game_id: dict[str, str] = {}
                install_path: dict[str, Path] = {}
                wine_prefix: dict[str, Path] = {}
                (
                    launcher["epic"],
                    game_id["epic"],
                    install_path["epic"],
                    wine_prefix["epic"],
                ) = (
                    "epic",
                    epic_data["game_id"],
                    Path(epic_data["install_path"]),
                    get_wine_prefix(epic_data["game_id"], dir),
                )
                (
                    launcher["gog"],
                    game_id["gog"],
                    install_path["gog"],
                    wine_prefix["gog"],
                ) = (
                    "gog",
                    gog_data["game_id"],
                    Path(gog_data["install_path"]),
                    get_wine_prefix(gog_data["game_id"], dir),
                )
            else:
                logger.trace(
                    f"No valid game data found in {dir}. Skipping this directory."
                )
                launcher, game_id, install_path, wine_prefix = (
                    None,
                    None,
                    None,
                    None,
                )
                continue

            # If some values are present but others are missing, treat as incomplete
            if any(
                v is None for v in (install_path, launcher, game_id, wine_prefix)
            ) and not all(
                v is None for v in (install_path, launcher, game_id, wine_prefix)
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

    global heroic_config
    heroic_config = (launcher, game_id, install_path, wine_prefix)
    logger.success(
        f"Successfully retrieved game data for {display} from Heroic config. game_id={game_id}, install_path={install_path}, wine_prefix={wine_prefix}"
    )
    var.heroic_config = heroic_config
    return heroic_config


def get_libraries(config_directory: Path) -> tuple[Path, Path]:
    """
    Gets Heroic game library directories from the configuration directory.

    Parameters
    ----------
    config_directory : Path
        The path to the Heroic configuration directory.

    Returns
    -------
    tuple[Path, Path]
        A tuple containing the install paths for Epic and GOG games, respectively.
    """
    gog_available = True
    epic_available = True

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

    if not var.game_info.launcher_ids.gog:
        gog_available = False
        logger.trace(
            "GOG launcher ID not found in game info. Marking GOG as unavailable."
        )
    else:
        gog_data["game_id"] = var.game_info.launcher_ids.gog
        gog_data["installed_json"] = config_directory / "gog_store" / "installed.json"
    if not var.game_info.launcher_ids.epic:
        epic_available = False
        logger.trace(
            "Epic launcher ID not found in game info. Marking Epic as unavailable."
        )
    else:
        epic_data["game_id"] = var.game_info.launcher_ids.epic
        epic_data["installed_json"] = (
            config_directory / "legendaryConfig" / "legendary" / "installed.json"
        )
    if not valid():
        return None

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
        return None

    if gog_available:
        with open(gog_data["installed_json"], "r", encoding="utf-8") as file:
            json = from_json(file.read()).get("installed", [])
            for item in json:
                if item.get("appName") == str(gog_data["game_id"]):
                    gog_data["json"] = item
                    break
        if gog_data.get("json"):
            gog_data["install_path"] = Path(gog_data["json"].get("install_path"))
        else:
            logger.warning(
                f"Game with GOG ID {gog_data['game_id']} not found in installed games list. Marking GOG as unavailable."
            )
            gog_available = False
        if not gog_data.get("install_path"):
            logger.warning(
                f"Unable to extract install_path from {gog_data['installed_json']}. Marking GOG as unavailable."
            )
            gog_available = False

    if epic_available:
        with open(epic_data["installed_json"], "r", encoding="utf-8") as file:
            json = from_json(file.read()).get(epic_data["game_id"], {})
        if json:
            epic_data["install_path"] = Path(json.get("install_path"))
        else:
            logger.warning(
                f"Game with Epic ID {epic_data['game_id']} not found in installed games list. Marking Epic as unavailable."
            )
            epic_available = False
        if not epic_data.get("install_path"):
            logger.warning(
                f"Unable to extract install_path from {epic_data['installed_json']}. Marking Epic as unavailable."
            )
            epic_available = False

    if not valid():
        return None

    logger.success(
        f"Successfully retrieved library paths from Heroic config. gog={gog_data.get('install_path')}, epic={epic_data.get('install_path')}"
    )
    return epic_data.get("install_path"), gog_data.get("install_path")


def get_wine_prefix(game_id: str | int, config_directory: Path) -> Path:
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
