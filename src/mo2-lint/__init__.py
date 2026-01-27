#!/usr/bin/env python3

import click
from pathlib import Path
import re
from step.load_game_info import get_launcher, get_library
from step.configure_prefix import prompt as prompt_prefix, configure as configure_prefix
from step.external_resources import download
from util.nexus.install_handler import install as install_handler
from util.redirector.install import install as install_redirector
from util.uninstall import uninstall as _uninstall
from util import state_file as state, variables as var
from util.state_file import match_instances, set_index, InstanceData
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
        if latest != str(var.version):
            version_parts = list(map(int, str(var.version).split(".")))
            latest_parts = list(map(int, latest.split(".")))
            if latest_parts > version_parts:
                logger.warning(
                    f"A new version of mo2-lint is available: {latest} (current: {var.version}). Please update to the latest version."
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

        # try:
        #     from urllib.request import urlretrieve

        #     Path("~/.config/mo2-lint/").expanduser().mkdir(parents=True, exist_ok=True)
        #     urlretrieve(
        #         f"https://raw.githubusercontent.com/Furglitch/modorganizer2-linux-installer/refs/heads/rewrite/configs/{config}",
        #         Path("~/.config/mo2-lint/", config).expanduser(),
        #     )
        #     logger.debug(f"Downloaded latest {config} from GitHub.")
        # except Exception as e:
        #     logger.error(f"Failed to download {config}: {e}")


def get_valid_games() -> dict:
    """
    Returns
    -------
    dict: Nexus IDs of supported games.
    """
    return var.game_info.keys()


game_list = None
plugin_list = None


def preload_lists():
    """
    Preloads game and plugin lists for --help text.
    """

    remove_loggers()
    var.load_game_info()
    var.load_resource_info()
    var.load_plugin_info()
    global game_list, plugin_list
    game_list = ", ".join(get_valid_games())
    plugin_list = ", ".join(var.plugin_info.keys())


preload_lists()


class CustomCommand(click.Command):
    def get_help(self, ctx):
        help_text = super().get_help(ctx)
        help_text = re.sub(r"\.\n\n(\W+)\[", r".\n\1CHOICES: [", help_text)
        help_text = re.sub(r"\nOptions:\s*\n", "\n  [OPTIONS]\n\n", help_text)
        return help_text


@click.version_option(version=var.version, prog_name="mo2-lint")
@click.help_option("-h", "--help", help="Show this message.")
@click.option(
    "--uninstall",
    "-u",
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
    add_loggers(log_level, "MO2-LINT")
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
    var.load_game_info(game_info_path)

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

    state.load_state_file()

    # Handle --list
    if list_instances:
        list = match_instances()
        for idx, inst in enumerate(list, start=1):
            print(
                f"[{idx}] Game: {inst.game}, Path: {inst.instance_path}, Script Extender: {'Yes' if inst.script_extender else 'No'}, Plugins: {', '.join(inst.plugins) if inst.plugins else 'None'}"
            )
        return

    # Handle --uninstall
    if uninstall:
        _uninstall(game, directory)
        state.write_state(False)
        return

    # Plugin validation
    if plugin:
        var.load_plugin_info()
        for p in plugin:
            if p not in var.plugin_info:
                raise click.BadArgumentUsage(
                    f"Invalid plugin specified: {p}. Available plugins are: {plugin_list}"
                )

    var.set_parameters(
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

    if state.check_instance(game, directory):
        state.choose_instance()

    state.current_instance = InstanceData(
        index=-1,
        nexus_slug=game,
        instance_path=directory,
        launcher=get_launcher(),
        launcher_ids=var.LauncherIDs.from_dict(var.game_info[game].launcher_ids),
        game_path=get_library(),
        game_executable=var.game_info[game].executable,
        script_extender=script_extender,
        plugins=list(plugin) if plugin else [],
    )
    set_index()

    prompt_prefix()
    configure_prefix()
    download()
    install_handler()
    install_redirector()

    state.write_state()
    logger.success("mo2-lint completed successfully.")


if __name__ == "__main__":
    main()
