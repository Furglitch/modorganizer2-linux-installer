#!/usr/bin/env python3

from loguru import logger
import os
from pathlib import Path
from pydantic_core import from_json

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
            logger.debug(f"Found {release} release. Heroic config located at {dir}")

            gog_result = get_gog_libraries(dir)
            epic_result = get_epic_libraries(dir)
            if gog_result and epic_result:
                # TODO Handle multiple installs through different runners
                logger.error(
                    "Both GOG and Epic libraries found. Functionality not yet implemented."
                )
                launcher, id, install, wine, prefix = None, None, None, None, None
            elif gog_result:
                launcher, id, install, wine, prefix = gog_result
            elif epic_result:
                launcher, id, install, wine, prefix = epic_result
            else:
                launcher, id, install, wine, prefix = None, None, None, None, None

            if any(
                v is None for v in (install, launcher, id, wine, prefix)
            ) and not all(v is None for v in (install, launcher, id, wine, prefix)):
                logger.warning(
                    "Received incomplete Heroic library data. Continuing to next config directory if available."
                )
                continue
            else:
                break
        else:
            logger.warning(f"Unable to find Heroic config at {dir}")

    logger.debug(
        f"Heroic library data: install={install}, release={release}, launcher={launcher}, id={id}, wine={wine}, prefix={prefix}"
    )
    return install, release, launcher, id, wine, prefix


def get_wine_variables(id: str | int, config_dir: str):
    config_json = Path(config_dir) / "GamesConfig" / f"{id}.json"
    if not config_json.exists():
        logger.error(f'Config JSON not found at "{config_json}"')
        return None

    failed = False
    try:
        with open(config_json, "r", encoding="utf-8") as file:
            data = from_json(file.read())
        wine_path = data.get(str(id), {}).get("wineVersion", {}).get("bin") or None
    except Exception as e:
        logger.warning(f"Failed to parse {config_json} for wine path: {e}")
        failed = True
    if failed:
        try:
            global_cfg = Path(config_dir) / "config.json"
            if global_cfg.exists():
                with open(global_cfg, "r", encoding="utf-8") as file:
                    data = from_json(file.read())
                wine_path = (
                    data.get("defaultSettings", {}).get("wineVersion", {}).get("bin")
                    or None
                )
            else:
                logger.error(f'Global config JSON not found at "{global_cfg}"')
                return None
        except Exception as e:
            logger.warning(f"Failed to parse {global_cfg} for wine version: {e}")
            return None
    logger.debug(f"Found wine path: {wine_path}")

    try:
        with open(config_json, "r", encoding="utf-8") as file:
            data = from_json(file.read())
        wine_prefix = data.get(str(id), {}).get("winePrefix", {}) or None
    except Exception as e:
        logger.warning(f"Failed to parse {config_json} for wine prefix: {e}")
        return None
    logger.debug(f"Found wine prefix: {wine_prefix}")

    return wine_path, wine_prefix


def get_gog_libraries(config_dir: str):
    installed_json = Path(config_dir) / "gog_store" / "installed.json"

    from util.variables import game_info

    if not game_info.get("gog_id", ""):
        logger.warning("GOG ID is not set for game.")
        return None
    if not installed_json.exists():
        logger.error(f'installed.json not found at "{installed_json}"')
        return None

    try:
        with open(installed_json, "r", encoding="utf-8") as file:
            data = from_json(file.read())
        logger.trace(f"Parsed GOG installed.json: {data}")
    except Exception as e:
        logger.error(f"Failed to parse {installed_json}: {e}")
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
    installed_json = (
        Path(config_dir) / "legendaryConfig" / "legendary" / "installed.json"
    )

    from util.variables import game_info

    if not game_info.get("epic_id", ""):
        logger.warning("Epic ID is not set for game.")
        return None
    if not installed_json.exists():
        logger.error(f'installed.json not found at "{installed_json}"')
        return None

    try:
        with open(installed_json, "r", encoding="utf-8") as file:
            data = from_json(file.read())
        logger.trace(f"Parsed Epic installed.json: {data}")
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
        logger.error("Could not retrieve Wine variables from config")
        return None
    wine_path, wine_prefix = wine_vars

    launcher = "epic"
    appid = game_info["epic_id"]
    return launcher, appid, install_path, wine_path, wine_prefix
