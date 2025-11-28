#!/usr/bin/env python3

from loguru import logger
import os
from pathlib import Path

launcher = None


def get_heroic_data():
    config_directories = [
        "${HOME}/.config/heroic",
        "${HOME}/.var/app/com.heroicgameslauncher.hgl/config/heroic",
    ]
    release_type = [
        "stable",
        "flatpak",
    ]

    for i, dir in enumerate(config_directories):
        release = release_type[i]
        dir = os.path.expandvars(dir)
        if os.path.exists(dir):
            logger.info(f"Found {release} release, Heroic config directory at {dir}")

            gog_result = get_gog_libraries(dir)
            epic_result = get_epic_libraries(dir)
            if gog_result:
                launcher, id, install, wine, prefix = gog_result
            elif epic_result:
                launcher, id, install, wine, prefix = epic_result
            elif gog_result and epic_result:
                logger.error("Both GOG and Epic libraries found, ambiguous.")
                launcher, id, install, wine, prefix = None, None, None, None, None
            else:
                launcher, id, install, wine, prefix = None, None, None, None, None
            if any(
                v is None for v in (install, launcher, id, wine, prefix)
            ) and not all(v is None for v in (install, launcher, id, wine, prefix)):
                logger.warning("Could not retrieve complete Heroic library data.")
                continue
            else:
                break
        else:
            logger.info(f"Heroic config directory not present at {dir}")

    logger.debug(
        f"Heroic library data: install={install}, release={release}, launcher={launcher}, id={id}, wine={wine}, prefix={prefix}"
    )
    return install, release, launcher, id, wine, prefix


def get_wine_variables(id: str | int, config_dir: str):
    """Retrieves Wine environment variables from product json."""
    config_json = Path(config_dir) / "GamesConfig" / f"{id}.json"
    if not config_json.exists():
        logger.error(f"{config_json} not found.")
        return None

    import json

    failed = False
    try:
        data = json.loads(config_json.read_text())
        wine_path = data.get(str(id), {}).get("wineVersion", {}).get("bin") or None
    except Exception as e:
        logger.debug(f"Failed to parse {config_json} for wine path: {e}")
        failed = True
    if failed:
        try:
            global_cfg = Path(config_dir) / "config.json"
            if global_cfg.exists():
                data = json.loads(global_cfg.read_text())
                wine_path = (
                    data.get("defaultSettings", {}).get("wineVersion", {}).get("bin")
                    or None
                )
            else:
                logger.error(f"{global_cfg} not found.")
                return None
        except Exception as e:
            logger.debug(f"Failed to parse {global_cfg} for wine version: {e}")
            return None
    logger.debug(f"Found wine path: {wine_path}")

    try:
        data = json.loads(config_json.read_text())
        wine_prefix = data.get(str(id), {}).get("winePrefix", {}) or None
    except Exception as e:
        logger.debug(f"Failed to parse {config_json} for wine prefix: {e}")
        return None
    logger.debug(f"Found wine prefix: {wine_prefix}")

    return wine_path, wine_prefix


def get_gog_libraries(config_dir: str):
    """Finds GOG library folders from Heroic configuration files."""
    installed_json = Path(config_dir) / "gog_store" / "installed.json"

    from util.variables import game_info

    if not game_info["gog_id"]:
        logger.warning(f"GOG ID for {game_info['display']} is not set.")
        return None
    if not installed_json.exists():
        logger.error(f"{installed_json} not found.")
        return None

    import json

    try:
        data = json.loads(installed_json.read_text())
        logger.debug(f"Parsed installed.json: {data}")
    except Exception as e:
        logger.error(f"Unable to parse {installed_json}: {e}")
        return None

    installed = data.get("installed", [])
    install_path = [
        item.get("install_path")
        for item in installed
        if item.get("install_path") and item.get("appName") == str(game_info["gog_id"])
    ]
    if not install_path:
        if any(item.get("appName") == str(game_info["gog_id"]) for item in installed):
            logger.error(f"Unable to extract install_path from {installed_json}")
        else:
            logger.warning("Game not found in installed GOG games.")
        return None
    logger.info(f"Found GOG install paths: {install_path}")

    wine_vars = get_wine_variables(game_info["gog_id"], config_dir)
    if not wine_vars:
        logger.error("Could not retrieve Wine variables")
        return None
    wine_path, wine_prefix = wine_vars

    launcher = "gog"
    appid = game_info["gog_id"]
    return launcher, appid, install_path, wine_path, wine_prefix


def get_epic_libraries(config_dir: str):
    """Finds Epic library folders from Heroic configuration files."""
    installed_json = (
        Path(config_dir) / "legendaryConfig" / "legendary" / "installed.json"
    )

    from util.variables import game_info

    if not game_info["epic_id"]:
        logger.warning(f"Epic ID for {game_info['display']} is not set.")
        return None
    if not installed_json.exists():
        logger.error(f"{installed_json} not found.")
        return None

    import json

    try:
        data = json.loads(installed_json.read_text())
        logger.debug(f"Parsed installed.json: {data}")
    except Exception as e:
        logger.error(f"Unable to parse {installed_json}: {e}")
        return None
    install_path = data.get(game_info["epic_id"], {}).get("install_path", "")
    if not install_path:
        if game_info["epic_id"] in data:
            logger.error(f"Unable to extract install_path from {installed_json}")
        else:
            logger.warning("Game not found in installed Epic games.")
        return None
    logger.info(f"Found Epic install paths: {install_path}")

    wine_vars = get_wine_variables(game_info["epic_id"], config_dir)
    if not wine_vars:
        logger.error("Could not retrieve Wine variables")
        return None
    wine_path, wine_prefix = wine_vars

    launcher = "epic"
    appid = game_info["epic_id"]
    return launcher, appid, install_path, wine_path, wine_prefix
