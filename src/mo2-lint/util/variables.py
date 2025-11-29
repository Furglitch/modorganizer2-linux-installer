#!/usr/bin/env python3

from pydantic_core import from_json
from pathlib import Path
from loguru import logger

parameters: dict = None
game_info: dict = None
launcher: str = None
heroic_runner: str = None
heroic_config: list = None
game_install_path: Path = None
scriptextender_url: str = None
scriptextender_nxm_modid: int = None
scriptextender_nxm_fileid: int = None
scriptextender_version: str = None
scriptextender_files: list = None
archived_prefix: Path = None


def gameinfo_path():
    path = Path(__file__).resolve().parents[3] / "configs" / "game_info.json"
    logger.trace(f"Game info path: {path}")
    return path


def load_gameinfo_file():
    """Returns the entire game_info.json content as a dictionary."""
    with open(gameinfo_path(), "r", encoding="utf-8") as file:
        json = from_json(file.read())
    logger.trace(f"Loaded game info file: {json}")
    return json


def load_gameinfo(gamekey: str):
    """Returns the game_info.json data for a specific game."""
    global game_info
    game_info = load_gameinfo_file().get(gamekey)
    logger.trace(f"Loaded game info for {gamekey}: {game_info}")
    return game_info


def set_parameters(params: dict):
    global parameters
    parameters = params
    logger.debug(f"Parameters have been set to: {parameters}")
