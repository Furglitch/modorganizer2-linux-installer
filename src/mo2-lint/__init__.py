#!/usr/bin/env python3

import click
import sys
from pydantic_core import from_json
from pathlib import Path
from loguru import logger

"""
Log Levels:
TRACE: Detailed debug info. Logfile level.
DEBUG: General debug info
INFO: General operational info. Default terminal level.
SUCCESS: Successful operation (including function completions)
WARNING: User error
ERROR: Operational error
CRITICAL: Fatal error
"""


def load_game_list():
    from util.variables import gameinfo_path

    with open(gameinfo_path(), "r", encoding="utf-8") as file:
        json = from_json(file.read())
        games = list(json.keys())
        logger.trace(f"Loaded game list: {games}")
    return games


@click.command()
@click.version_option(version="1.0.0", prog_name="mo2-lint")
@click.help_option("-h", "--help")
@click.argument(
    "game", type=click.Choice(load_game_list(), case_sensitive=False), required=True
)
@click.argument(
    "directory",
    type=click.Path(file_okay=False, dir_okay=True),
    required=True,
)
@click.option(
    "--log-level",
    "-l",
    type=click.Choice(["DEBUG", "INFO", "TRACE"], case_sensitive=False),
    default="INFO",
    help="Set the logging level.",
    show_default=True,
)
@click.option(
    "--script-extender",
    "-s",
    is_flag=True,
    default=False,
    help="Automatically download and install script extenders if available.",
)
@click.option(
    "--plugin",
    "-p",
    type=str,
    multiple=True,
    help="Specify MO2 plugins to download and install.",
)
def main(game, directory, log_level, script_extender, plugin):
    """A tool to install and manage Mod Organizer 2 instances for games from Steam and Heroic Games Launcher."""

    logger.remove(0)
    logger.add(
        sys.stdout,
        colorize=True,
        format="<green>{time}</green> | <level>{level}</level> | {message}",
        level=log_level,
    )
    logger.add(
        "mo2-lint.{time:YYYY-MM-DD_HH-mm-ss}.log",  # "~/.cache/mo2-lint/logs/install.{time:YYYY-MM-DD_HH-mm-ss}.log"
        level="TRACE",
        rotation="10 MB",
        retention="7 days",
        compression="zip",
    )
    logger.info("Starting mo2-lint...")

    if not Path(directory).exists():
        Path(directory).mkdir(parents=True, exist_ok=True)

    from util.variables import set_parameters

    set_parameters(
        {
            "game": game,
            "directory": directory,
            "log_level": log_level,
            "script_extender": script_extender,
            "plugins": plugin,
        }
    )

    from step.load_gameinfo import main as load_gameinfo

    load_gameinfo()

    from step.configure_prefix import main as configure_prefix

    configure_prefix()

    from step.external_resources import main as external_resources

    external_resources()


if __name__ == "__main__":
    main()
