#!/usr/bin/env python3

from pydantic_core import from_json
from pathlib import Path
from loguru import logger

parameters: dict = None
game_info: dict = None
resource_info: dict = None
launcher: str = None
prefix: Path = None
heroic_runner: str = None
heroic_config: list = None
game_install_path: Path = None
scriptextender_url: str = None
scriptextender_nxm_modid: int = None
scriptextender_nxm_fileid: int = None
scriptextender_version: str = None
scriptextender_files: list = None
scriptextender_checksum: str = None
archived_prefix: Path = None


def gameinfo_path():
    path = (
        Path(__file__).resolve().parents[3] / "configs" / "game_info.json"
    )  # TODO Change path to .config
    logger.trace(f"Game info path: {path}")
    return path


def resourceinfo_path():
    path = (
        Path(__file__).resolve().parents[3] / "configs" / "resource_info.json"
    )  # TODO Change path to .config
    logger.trace(f"Resource info path: {path}")
    return path


def plugininfo_path():
    path = (
        Path(__file__).resolve().parents[3] / "configs" / "plugin_info.json"
    )  # TODO Change path to .config
    logger.trace(f"Plugin info path: {path}")
    return path


def load_gameinfo_file():
    with open(gameinfo_path(), "r", encoding="utf-8") as file:
        json = from_json(file.read())
    logger.trace(f"Loaded game info file: {json}")
    return json


def load_gameinfo(gamekey: str):
    global game_info
    game_info = load_gameinfo_file().get(gamekey)
    logger.trace(f"Loaded game info for {gamekey}: {game_info}")
    return game_info


def load_resourceinfo():
    global resource_info
    with open(resourceinfo_path(), "r", encoding="utf-8") as file:
        resource_info = from_json(file.read())
    logger.trace(f"Loaded resource info: {resource_info}")
    return resource_info


def load_plugininfo():
    global plugin_info
    with open(plugininfo_path(), "r", encoding="utf-8") as file:
        plugin_info = from_json(file.read())
    logger.trace(f"Loaded plugin info file: {plugin_info}")
    return plugin_info


def set_parameters(params: dict):
    global parameters
    parameters = params
    logger.debug(f"Parameters have been set to: {parameters}")
