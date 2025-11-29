#!/usr/bin/env python3

from pydantic_core import from_json
from pathlib import Path
from loguru import logger

parameters = {}
game_info = None
launcher = None
heroic_runner = None
heroic_config = []
game_install_path = None
scriptextender_url = None
scriptextender_nxm_modid = None
scriptextender_nxm_fileid = None
scriptextender_version = None
scriptextender_files = []


def gameinfo_path():
    return Path(__file__).resolve().parents[3] / "configs" / "game_info.json"


def load_gameinfo_file():
    """Returns the entire game_info.json content as a dictionary."""
    with open(gameinfo_path(), "r", encoding="utf-8") as file:
        json = from_json(file.read())
    logger.debug(f"Loaded game info file: {json}")
    return json


def load_gameinfo(gamekey: str):
    """Returns the game_info.json data for a specific game."""
    global game_info
    game_info = load_gameinfo_file().get(gamekey)
    logger.debug(f"Loaded game info for {gamekey}: {game_info}")
    return game_info


def set_parameters(params: dict):
    global parameters
    parameters = params
    logger.debug(f"Parameters have been set to: {parameters}")
