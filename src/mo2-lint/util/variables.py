#!/usr/bin/env python3

from pydantic_core import from_json
from pathlib import Path
from loguru import logger

version = "7.0.0"

parameters: dict = None
game_info: dict = None
resource_info: dict = None
launcher: str = None
prefix: Path = None
heroic_runner: str = None
heroic_config: list = None
game_install_path: Path = None
archived_prefix: Path = None


def internal_file(*parts):
    import sys

    path = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve()))
    return path.joinpath(*parts)


def internal_path(file: str):
    if not Path("~/.config/mo2-lint/", file).expanduser().exists():
        path = internal_file("cfg", file)
    else:
        path = Path("~/.config/mo2-lint/", file).expanduser()
    logger.trace(f"{file} path: {path}")
    return path


def load_gameinfo_file(path: Path):
    with open(path, "r", encoding="utf-8") as file:
        json = from_json(file.read())
    logger.trace(f"Loaded game info file: {json}")
    return json


def load_gameinfo(gamekey: str, path: str = None):
    global game_info
    if not path:
        path = internal_path("game_info.json")
    game_info = load_gameinfo_file(Path(path)).get(gamekey)
    logger.trace(f"Loaded game info for {gamekey}: {game_info}")
    return game_info


def load_resourceinfo():
    global resource_info
    with open(internal_path("resource_info.json"), "r", encoding="utf-8") as file:
        resource_info = from_json(file.read())
    logger.trace(f"Loaded resource info: {resource_info}")
    return resource_info


def load_plugininfo():
    global plugin_info
    with open(internal_path("plugin_info.json"), "r", encoding="utf-8") as file:
        plugin_info = from_json(file.read())
    logger.trace(f"Loaded plugin info file: {plugin_info}")
    return plugin_info


def set_parameters(params: dict):
    global parameters
    parameters = params
    logger.debug(f"Parameters have been set to: {parameters}")
