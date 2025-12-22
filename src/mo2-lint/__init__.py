#!/usr/bin/env python3

import click
from pydantic_core import from_json
from pathlib import Path
from loguru import logger
from step import configure_prefix, load_gameinfo, external_resources
from util.nexus import install_handler
import util.state.state_file as state

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


def pull_config():
    configs = {"game_info.json", "resource_info.json", "plugin_info.json"}
    for config in configs:
        # Pull defaults from internal if not present in .config
        if not Path("~/.config/mo2-lint/", config).expanduser().exists():
            logger.debug(
                f"{config} not found in ~/.config/mo2-lint/, copying default from internal files."
            )
            from shutil import copy2
            from util.variables import internal_file

            src = internal_file("cfg", config)
            dest = Path("~/.config/mo2-lint/", config).expanduser()
            dest.parent.mkdir(parents=True, exist_ok=True)
            copy2(src, dest)
            logger.debug(f"Copied default {config} to ~/.config/mo2-lint/")
        # Download latest from GitHub
        try:
            from urllib.request import urlretrieve

            Path("~/.config/mo2-lint/").expanduser().mkdir(parents=True, exist_ok=True)
            urlretrieve(
                f"https://raw.githubusercontent.com/Furglitch/modorganizer2-linux-installer/refs/heads/rewrite/configs/{config}",
                Path("~/.config/mo2-lint/", config).expanduser(),
            )
            logger.debug(f"Downloaded latest {config} from GitHub.")
        except Exception as e:
            logger.error(f"Failed to download {config}: {e}")


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
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | {message}",
        level=log_level,
    )

    filename = Path(
        "~/.cache/mo2-lint/logs/install.{time:YYYY-MM-DD_HH-mm-ss}.log"
    ).expanduser()
    logout = logger.add(
        filename,
        level="TRACE",
        rotation="10 MB",
        retention="7 days",
        compression="zip",
    )


def load_game_list():
    from util.variables import path

    set_logger("TRACE")
    pull_config()
    with open(path("game_info.json"), "r", encoding="utf-8") as file:
        json = from_json(file.read())
        games = list(json.keys())
        logger.trace(f"Loaded game list: {games}")
    return games


@click.command()
@click.version_option(version="7.0.0", prog_name="mo2-lint")
@click.help_option("-h", "--help")
@click.argument(
    "game",
    type=click.Choice(load_game_list(), case_sensitive=False),
    required=True,
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
    set_logger(log_level.upper())
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

    state.load_state()
    state.check_existing_instances(directory, game)
    state.select_index()
    state.set_nexus_id(game)
    state.set_instance_path(directory)
    state.set_plugins(list(plugin))

    load_gameinfo.main()
    configure_prefix.main()
    external_resources.main()
    install_handler.main()

    state.write_state()


if __name__ == "__main__":
    main()
