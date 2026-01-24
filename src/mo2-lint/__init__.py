#!/usr/bin/env python3

import click
from pydantic_core import from_json
from pathlib import Path
from step import configure_prefix, load_gameinfo, external_resources
from util import uninstall as uninstall_instance
from util.nexus import install_handler
from util.redirector import install as install_redirector
from util.state import state_file as state, state_list
from util.variables import version
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


def check_updates():
    # Checks for updates from https://github.com/Furglitch/modorganizer2-linux-installer
    import requests

    try:
        response = requests.get(
            "https://api.github.com/repos/Furglitch/modorganizer2-linux-installer/releases/latest"
        )
        git_version = response.json()["tag_name"]
        if git_version != str(version):
            git_parts = list(map(int, git_version.split(".")))
            version_parts = list(map(int, str(version).split(".")))
            if git_parts > version_parts:
                logger.warning(
                    f"A new version of mo2-lint is available: {git_version} (current: {version}). Please update to the latest version."
                )
    except Exception as e:
        logger.error(f"Failed to check for updates: {e}")


def pull_config():
    import sys

    remove_loggers()

    # Get log level
    if any(arg in sys.argv for arg in ["--log-level", "-l"]):
        log_index = (
            sys.argv.index("--log-level")
            if "--log-level" in sys.argv
            else sys.argv.index("-l")
        )
        if log_index + 1 < len(sys.argv):
            log_level = sys.argv[log_index + 1].upper()
            add_loggers(log_level)
    # Silence if --list or --uninstall is used
    elif any(arg in sys.argv for arg in ["--list", "-L", "--uninstall", "-U"]):
        add_loggers("ERROR")
    else:
        add_loggers("INFO")

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


game_list = []


def load_game_list():
    from util.variables import internal_path as path

    pull_config()
    with open(path("game_info.json"), "r", encoding="utf-8") as file:
        json = from_json(file.read())
        games = list(json.keys())
        logger.trace(f"Loaded game list: {games}")
    global game_list
    game_list = ", ".join(sorted(games))
    return games


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
    "--script-extender",
    "-s",
    is_flag=True,
    default=False,
    help="Automatically install script extenders (if available).",
)
@click.option(
    "--plugin",
    "-p",
    type=str,
    multiple=True,
    help="Specify MO2 plugins to download and install.",
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
    "--custom",
    "-c",
    "custom",
    is_flag=True,
    default=False,
    help="Use a custom game_info file to install for any game.\nRequires [GAME], [DIRECTORY], [GAMEINFO] arguments.\nUnsupported.",
)
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
@click.argument(
    "gameinfo_path",
    required=False,
    type=click.Path(file_okay=True, dir_okay=False),
    metavar="[GAMEINFO]",
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
    [GAMEINFO]                      Path to custom game_info JSON file. Only needed if --custom is used.\n
    """,
)
def main(
    custom,
    game,
    directory,
    gameinfo_path,
    log_level,
    script_extender,
    plugin,
    list_instances,
    uninstall,
):
    if not (custom or list_instances or uninstall):
        if game not in load_game_list():
            logger.critical(
                f"Invalid game specified: {game}. Available games are: {game_list}"
            )
            raise SystemExit(1)

    logger.info("Starting mo2-lint...")
    check_updates()

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

    if list_instances:
        state_list.main()
        return
    elif uninstall:
        uninstall_instance.main(game)
        return
    elif not directory or not game:
        raise click.BadArgumentUsage(
            "GAME and DIRECTORY arguments are required unless --list or --uninstall is used."
        )

    if not Path(directory).exists():
        Path(directory).mkdir(parents=True, exist_ok=True)

    state.check_existing_instances(directory, game)
    state.select_index()
    state.set_nexus_id(game)
    state.set_instance_path(directory)
    state.set_plugins(list(plugin))

    load_gameinfo.main() if not custom else load_gameinfo.main(
        custom_game_info_path=gameinfo_path
    )
    configure_prefix.main()
    external_resources.main()
    install_handler.main()
    install_redirector.main()

    state.write_state()


if __name__ == "__main__":
    main()
