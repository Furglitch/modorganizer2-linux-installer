#!/usr/bin/env python3

import click
import sys
from pydantic_core import from_json
from pathlib import Path
from util.variables import gameinfo_path, set_parameters
from loguru import logger


def load_game_list():
    with open(gameinfo_path(), "r", encoding="utf-8") as file:
        json = from_json(file.read())
    return list(json.keys())


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
    type=click.Choice(["DEBUG", "INFO"], case_sensitive=False),
    default="INFO",
    help="Set the logging level.",
    show_default=True,
)
@click.option(
    "--script-extender",
    "-s",
    type=bool,
    help="Enable download of script extenders for supported games.",
)
@click.option(
    "--plugin",
    "-p",
    type=str,
    multiple=True,
    help="Specify MO2 plugins to download and install.",
)
def main(game, directory, log_level, script_extender, plugin):
    """A tool to install and manage Mod Organizer 2 instances."""

    logger.remove(0)
    logger.add(
        sys.stdout,
        colorize=True,
        format="<green>{time}</green> | <level>{level}</level> | {message}",
        level=log_level,
    )
    logger.add(
        "mo2-lint.{time:YYYY-MM-DD_HH-mm-ss}.log",
        rotation="10 MB",
        retention="7 days",
        compression="zip",
    )
    logger.info("Starting mo2-lint...")

    logger.info(f"Selected game: {game}")
    logger.info(f"Target directory: {directory}")

    if not Path(directory).exists():
        Path(directory).mkdir(parents=True, exist_ok=True)

    set_parameters(
        {
            "game": game,
            "directory": directory,
            "script_extender": script_extender,
            "plugins": plugin,
        }
    )

    from step.load_gameinfo import main as load_gameinfo

    load_gameinfo()


if __name__ == "__main__":
    main()
