#!/usr/bin/env python3

import click
from pathlib import Path
from step import configure_prefix, external_resources
from util.nexus import install_handler
from util.redirector import install as install_redirector
from util.state import state_file as state, state_list
from util.variables import (
    set_parameters,
    load_game_info,
    load_plugin_info,
    version,
    game_info,
    plugin_info,
)
from util.logger import add_loggers, remove_loggers
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


def check_update() -> None:
    import requests

    try:
        response = requests.get(
            "https://api.github.com/repos/Furglitch/modorganizer2-linux-installer/releases/latest"
        ).json()
        latest = response["tag_name"]
        if latest != str(version):
            version_parts = list(map(int, str(version).split(".")))
            latest_parts = list(map(int, latest.split(".")))
            if latest_parts > version_parts:
                logger.warning(
                    f"A new version of mo2-lint is available: {latest} (current: {version}). Please update to the latest version."
                )
                return
    except Exception as e:
        logger.error(f"Failed to check for updates: {e}")
        return
    logger.debug("mo2-lint is up to date.")


def pull_config() -> None:
    """
    Attempts to pull the latest configuration files from GitHub.

    Before that, copies default configuration files from internal storage if not already present.
    """
    for config in {"game_info.json", "resource_info.json", "plugin_info.json"}:
        if not Path("~/.config/mo2-lint/", config).expanduser().exists():
            logger.debug(f"{config} not found in ~/.config/mo2-lint/")
            from shutil import copy2
            from util.internal_file import internal_file

            src = internal_file("cfg", config)
            dest = Path("~/.config/mo2-lint/", config).expanduser()
            dest.parent.mkdir(parents=True, exist_ok=True)
            copy2(src, dest)
            logger.debug(f"Copied default {config} to ~/.config/mo2-lint/")

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


def get_valid_games() -> dict:
    """
    Returns
    -------
    dict: Nexus IDs of supported games.
    """
    return game_info.keys()


game_list = None
plugin_list = None


def preload_lists():
    """
    Preloads game and plugin lists for --help text.
    """

    remove_loggers()
    load_game_info()
    load_plugin_info()
    global game_list, plugin_list
    game_list = ", ".join(get_valid_games())
    plugin_list = ", ".join(plugin_info.keys())


preload_lists()


class CustomCommand(click.Command):
    def get_help(self, ctx):
        import re

        help_text = super().get_help(ctx)
        help_text = re.sub(r"\.\n\n(\W+)\[", r".\n\1CHOICES: [", help_text)
        help_text = re.sub(r"\nOptions:\s*\n", "\n  [OPTIONS]\n\n", help_text)
        return help_text


@click.version_option(version=version, prog_name="mo2-lint")
@click.help_option("-h", "--help", help="Show this message.")
@click.option(
    "--uninstall",
    "-U",
    "uninstall",
    is_flag=True,
    default=False,
    help="Choose to uninstall a Mod Organizer 2 instance instead of installing.\n[GAME] and [DIRECTORY] arguments are optional.",
)
@click.option(
    "--list",
    "-L",
    "list_instances",
    is_flag=True,
    default=False,
    help="List existing instances of Mod Organizer 2.\nDoes not require [GAME] or [DIRECTORY] arguments.",
)
@click.option(
    "--plugin",
    "-p",
    type=str,
    multiple=True,
    help=f"Specify MO2 plugins to download and install.\nCHOICES: [{plugin_list}]",
)
@click.option(
    "--script-extender",
    "-s",
    is_flag=True,
    default=False,
    help="Automatically install script extenders (if available).",
)
@click.option(
    "--custom",
    "-c",
    "game_info_path",
    type=click.Path(file_okay=True, dir_okay=False, path_type=Path),
    help=(
        "Use a custom game_info file to install for any game. Follow with '/path/to/game_info.json'. "
        "Requires [GAME], [DIRECTORY] arguments. MO2 installs for custom games unsupported"
    ),
)
@click.option(
    "--log-level",
    "-l",
    "log_level",
    default="INFO",
    type=click.Choice(["DEBUG", "INFO", "TRACE"], case_sensitive=False),
    show_default=True,
    help="Set the logging level.",
)
@click.argument(
    "directory",
    required=False,
    type=click.Path(file_okay=False, dir_okay=True),
)
@click.argument(
    "game",
    required=False,
    type=str,
    metavar="[GAME]",
)
@click.command(
    cls=CustomCommand,
    help=f"""
    [GAME]                          The game to configure Mod Organizer 2 for.\n
                                    [{game_list}]\n
    [DIRECTORY]                     Mod Organizer 2 install path.\n
    """,
)
def main(
    game,
    directory,
    game_info_path,
    log_level,
    script_extender,
    plugin,
    list_instances,
    uninstall,
):
    # Pre-init setup
    remove_loggers()
    add_loggers(log_level, "MO2-LINT") if not (
        list_instances or uninstall
    ) else add_loggers("ERROR", "MO2-LINT")
    logger.info("Starting mo2-lint")
    check_update()
    pull_config()
    if isinstance(directory, str):
        directory = Path(directory)
    if isinstance(game_info_path, str):
        game_info_path = Path(game_info_path)

    # Game info loading and selection validation
    if game_info_path:
        if not game_info_path.exists():
            raise FileNotFoundError(
                f"Custom game_info file not found: {game_info_path}"
            )
    else:
        game_info_path = None
    load_game_info(game_info_path)

    if list_instances or uninstall:
        pass
    elif not game or not directory:
        raise click.BadArgumentUsage(
            "GAME and DIRECTORY arguments are required unless --list or --uninstall is used."
        )
    elif game not in game_list:
        raise click.BadArgumentUsage(
            f"Invalid game specified: {game}. Available games are: {game_list}"
        )

    state.load_state()

    # Handle --list
    if list_instances:
        state_list.main()
        return

    # Handle --uninstall
    if uninstall:
        from util import _uninstall

        _uninstall.main(game, directory)
        return

    # Plugin validation
    if plugin:
        load_plugin_info()
        for p in plugin:
            if p not in plugin_info:
                raise click.BadArgumentUsage(
                    f"Invalid plugin specified: {p}. Available plugins are: {plugin_list}"
                )

    set_parameters(
        {
            "game": game,
            "directory": directory,
            "game_info_path": game_info_path,
            "log_level": log_level,
            "script_extender": script_extender,
            "plugins": plugin,
        }
    )
    Path(directory).mkdir(parents=True, exist_ok=True)

    state.check_existing_instances(directory, game)
    state.select_index()
    state.set_nexus_id(game)
    state.set_instance_path(directory)
    state.set_plugins(list(plugin))

    configure_prefix.main()
    external_resources.main()
    install_handler.main()
    install_redirector.main()

    state.write_state()

    logger.success("mo2-lint completed successfully.")

    pass


if __name__ == "__main__":
    main()
