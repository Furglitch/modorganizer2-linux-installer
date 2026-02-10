#!/usr/bin/env python3

from loguru import logger
from pathlib import Path
from typing import Optional
from util import lang
from util.state_file import match_instances


def list(game: Optional[str], directory: Optional[Path]):
    matched = match_instances(game, directory)
    if not matched:
        logger.error(f"No MO2 instance found for game={game}, directory={directory}")
        return
    type = "matching " if (game or directory) else ""
    logger.success(f"Found {len(matched)} {type}Mod Organizer 2 instance(s)")
    matched_list = lang.list_instances(matched)
    for item in matched_list:
        logger.info(f"  - {item}")
