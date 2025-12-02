#!/usr/bin/env python3

import click
from pathlib import Path
from loguru import logger
from pydantic_core import from_json

stdout = None
logout = None


def set_logger(log_level):
    import sys

    global stdout, logout

    logger.remove(stdout)
    logger.remove(logout)

    stdout = logger.add(
        sys.stdout,
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <bold>Heroic Install Finder</bold> | {message}",
        level=log_level,
    )

    filename = Path(
        "~/.cache/mo2-lint/logs/heroic-install-finder.{time:YYYY-MM-DD_HH-mm-ss}.log"
    ).expanduser()
    logout = logger.add(
        filename,
        level="TRACE",
        rotation="10 MB",
        retention="7 days",
        compression="zip",
    )


def get_heroic_data(gog_id: int = None, epic_id: str = None):
    config_directories = [
        "${HOME}/.config/heroic",
        "${HOME}/.var/app/com.heroicgameslauncher.hgl/config/heroic",
    ]
    release_type = [
        "stable",
        "flatpak",
    ]

    import os

    for i, dir in enumerate(config_directories):
        release = release_type[i]
        dir = os.path.expandvars(dir)
        if os.path.exists(dir):
            logger.debug(f"Found {release} release. Heroic config located at {dir}")

            gog_result = get_gog_libraries(gog_id, dir)
            epic_result = get_epic_libraries(epic_id, dir)
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


def get_gog_libraries(id: int, config_dir: str):
    installed_json = Path(config_dir) / "gog_store" / "installed.json"

    if not id:
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
        if item.get("install_path") and item.get("appName") == str(id)
    ]
    if not install_path:
        if any(item.get("appName") == str(id) for item in installed):
            logger.error(f"Unable to extract install_path from {installed_json}")
        else:
            logger.warning("Game not found in installed GOG games.")
        return None
    logger.info(f"Found GOG install paths: {install_path}")

    wine_vars = get_wine_variables(id, config_dir)
    if not wine_vars:
        logger.error("Could not retrieve Wine variables")
        return None
    wine_path, wine_prefix = wine_vars

    launcher = "gog"
    appid = id
    return launcher, appid, install_path, wine_path, wine_prefix


def get_epic_libraries(id: str, config_dir: str):
    installed_json = (
        Path(config_dir) / "legendaryConfig" / "legendary" / "installed.json"
    )

    if not id:
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
    install_path = data.get(id, {}).get("install_path", "")
    if not install_path:
        if id in data:
            logger.error(f"Unable to extract install_path from {installed_json}")
        else:
            logger.warning("Game not found in installed Epic games.")
        return None
    logger.info(f"Found Epic install paths: {install_path}")

    wine_vars = get_wine_variables(id, config_dir)
    if not wine_vars:
        logger.error("Could not retrieve Wine variables from config")
        return None
    wine_path, wine_prefix = wine_vars

    launcher = "epic"
    appid = id
    return launcher, appid, install_path, wine_path, wine_prefix


@click.command()
@click.version_option(version="1.0.0", prog_name="mo2-lint")
@click.help_option("-h", "--help")
@click.option(
    "--log-level",
    "-l",
    type=click.Choice(["DEBUG", "INFO", "TRACE"], case_sensitive=False),
    default="INFO",
    help="Set the logging level.",
    show_default=True,
)
@click.option(
    "--gog-id",
    type=int,
    required=False,
    help="The GOG ID of the game to find the installation for.",
)
@click.option(
    "--epic-id",
    type=str,
    required=False,
    help="The Epic ID of the game to find the installation for.",
)
def main(log_level="INFO", gog_id: int = None, epic_id: str = None):
    """A handler for Nexus Mods URLs to interact with Mod Organizer 2 instances that are managed by mo2-lint. (Enables the 'Mod Manager Download' button on mod pages.)"""
    set_logger(log_level.upper())
    install, release, launcher, id, wine, prefix = get_heroic_data(gog_id, epic_id)
    out = {
        "install": install,
        "release": release,
        "launcher": launcher,
        "id": id,
        "wine": wine,
        "prefix": prefix,
    }
    import json

    print(json.dumps(out))  # Output for use in handler
    return install, release, launcher, id, wine, prefix


if __name__ == "__main__":
    main()
