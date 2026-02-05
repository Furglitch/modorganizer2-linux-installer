#!/usr/bin/env python3

from loguru import logger
from pathlib import Path
from pydantic_core import from_json
from typing import Optional
from util import lang, state_file as state, variables as var
from util.logger import add_loggers, remove_loggers
from command.install import install as _install
from command.uninstall import uninstall as _uninstall
from command.list import list as _list
from command.pin import pin as _pin
from command.update import update as _update
import click
import re
import yaml


def check_update():
    import requests

    logger.trace("Starting update check for mo2-lint.")
    try:
        logger.trace("Sending request to GitHub releases API.")
        response = from_json(
            requests.get(
                "https://api.github.com/repos/Furglitch/modorganizer2-linux-installer/releases/latest"
            ).text
        )
        latest = response["tag_name"]
        logger.trace(
            f"Latest version from GitHub: {latest}, current version: {var.version}"
        )
        if latest != str(var.version):
            version_parts = str(var.version).split(".")
            latest_parts = latest.split(".")
            logger.trace(
                f"Parsed version parts: current={version_parts}, latest={latest_parts}"
            )
            if tuple(latest_parts) > tuple(version_parts):
                logger.warning(
                    f"A new version of mo2-lint is available: {latest} (current: {var.version})."
                )
                return
    except Exception as e:
        logger.exception(
            f"Failed to check for updates: {e}", backtrace=True, diagnose=True
        )
        return
    logger.debug("mo2-lint is up to date.")


def pull_config():
    """
    Attempts to pull the latest configuration files from GitHub.

    Before that, copies default configuration files from internal storage if not already present.
    """
    logger.trace("Starting pull_config process.")
    for config in {"game_info.yml", "resource_info.yml", "plugin_info.yml"}:
        logger.trace(f"Processing config file: {config}")
        config_path = Path("~/.config/mo2-lint/", config).expanduser()
        dest = None
        if not config_path.exists():
            logger.debug(f"{config} not found in ~/.config/mo2-lint/")
            logger.trace(f"Copying default {config} from internal storage.")
            from shutil import copy2
            from util.internal_file import internal_file

            src = internal_file("cfg", config)
            dest = config_path
            dest.parent.mkdir(parents=True, exist_ok=True)
            copy2(src, dest)
            logger.debug(f"Copied default {config} to ~/.config/mo2-lint/")
        else:
            logger.trace(f"{config} already exists in ~/.config/mo2-lint/")

        # Check if yml schema version is incompatbile (remote yaml has higher version number than local script)
        remote_raw = f"https://raw.githubusercontent.com/Furglitch/modorganizer2-linux-installer/refs/heads/rewrite/configs/{config}"

        try:
            from urllib.request import urlretrieve
            from requests import get

            # Check remote schema version
            logger.trace(f"Checking remote schema version for {config}.")
            response = get(remote_raw)
            remote_yml = yaml.load(response.text, Loader=yaml.SafeLoader)
            remote_schema_version = remote_yml.get("schema", 0)
            remote_schema_parts = str(remote_schema_version).split(".")
            local_version_parts = str(var.version).split(".")
            logger.trace(
                f"Remote schema version: {remote_schema_version}, local version: {var.version}"
            )
            if tuple(remote_schema_parts) > tuple(local_version_parts):
                logger.warning(
                    f"There has been a schema update {config} which is incompatible with this version of mo2-lint. "
                    "The latest configuration files will not be downloaded. Please update mo2-lint to the latest version to continue receiving updates."
                )
            else:
                logger.trace(f"Attempting to download latest {config} from GitHub.")
                config_path.parent.mkdir(parents=True, exist_ok=True)
                urlretrieve(
                    remote_raw,
                    config_path,
                )
                logger.debug(
                    f"Downloaded latest {config} from GitHub to {config_path}."
                )
        except Exception as e:
            logger.exception(
                f"Failed to download {config}: {e}", backtrace=True, diagnose=True
            )


game_list = None
plugin_list = None


def pre_init():
    """
    Performs pre-initialization tasks such as loading game and plugin information
    and setting up logging. This is used to prepare help texts and command validation.
    """
    remove_loggers()
    add_loggers("INFO")
    logger.info("Starting mo2-lint...")
    check_update()
    pull_config()
    var.load_games_info()
    var.load_resource_info()
    var.load_plugin_info()
    global game_list, plugin_list
    game_list = ", ".join(var.games_info.keys())
    plugin_list = ", ".join(var.plugin_info.keys())


pre_init()


def start(
    game: Optional[str] = None,
    directory: Optional[Path | str] = None,
    game_info_path: Optional[Path | str] = None,
    log_level: Optional[str] = "INFO",
):
    """
    Common start routine for commands.
    Sets up logging, loads game information, and loads the state file.

    Parameters:
    -----------
    game : str, optional
        The target game for the Mod Organizer 2 instance.
    directory : Path | str, optional
        The target directory for the Mod Organizer 2 instance.
    game_info_path : Path | str, optional
        Path to a custom game_info.yml file.
    log_level : str, optional
        The logging level to set. Defaults to "INFO".
    """
    remove_loggers()
    add_loggers(log_level)
    if directory:
        directory = Path(directory)
    if game:
        load_game_info(game, game_info_path)
        if game not in var.games_info:
            raise click.BadArgumentUsage(
                f"Invalid game specified: {game}. Available games are: {game_list}"
            )
    state.load_state_file()


# Helper Functions
def load_game_info(game: Optional[str], game_info_path: Optional[Path]):
    """
    Loads game information, both broad and specific to the target game.

    Parameters:
    -----------
    game : str, optional
        The target game for which to load game_info.
    game_info_path : Path | str, optional
        Path to a custom game_info.yml file.
    """
    if game_info_path:
        if not game_info_path.exists():
            logger.error(f"Custom game_info file not found: {game_info_path}")
            logger.error("Defaulting to standard game_info.")
        else:
            logger.info(f"Loading custom game_info from: {game_info_path}")
    var.load_games_info(game_info_path)
    var.load_game_info(game)


click_version = click.version_option(version=var.version, prog_name="mo2-lint")
click_help = click.help_option("-h", "--help", help="Show this message.")
click_log_level = click.option(
    "--log-level",
    "-l",
    "log_level",
    type=click.Choice(["DEBUG", "INFO", "TRACE"], case_sensitive=False),
    default="INFO",
    show_default=True,
    help="Set the logging level.",
)
click_opt_game_info = click.option(
    "--custom",
    "game_info_path",
    type=click.Path(file_okay=True, dir_okay=False),
    help="Use a custom game_info.yml file.",
)
click_opt_game = click.option(
    "--game",
    "-g",
    type=str,
    help=f"Target game for the Mod Organizer 2 instance.\nOptions: [{game_list}]",
)
click_opt_directory = click.option(
    "--directory",
    "-d",
    type=click.Path(file_okay=False, dir_okay=True),
    help="Target install path for the Mod Organizer 2 instance.",
)


def click_arg_directory(required=False):
    return click.argument(
        "directory",
        required=required,
        type=click.Path(file_okay=False, dir_okay=True),
        metavar="[DIRECTORY]",
    )


def click_arg_game(required=False):
    return click.argument(
        "game",
        required=required,
        type=str,
        metavar="[GAME]",
    )


class CustomCommand(click.Command):  # Move [OPTIONS] to the end in the full help text
    class MoveOptions(click.Command):
        def get_help(self, ctx):
            usage = super().get_help(ctx)
            usage = usage.replace(" [OPTIONS]", "", 1)
            m = re.search(r"^(Usage: .+?)\n", usage, flags=re.M)
            if m:
                start, end = m.span(1)
                usage = usage[:end] + " [OPTIONS]" + usage[end:]
            return usage


@click.group()
@click.pass_context
def cli(ctx):
    ctx.ensure_object(dict)


@cli.command(
    cls=CustomCommand.MoveOptions, help=lang.help_install.format(list=game_list)
)
@click_version
@click_help
@click_log_level
@click_opt_game_info
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
@click_arg_game(required=True)
@click_arg_directory(required=True)
def install(
    game: str,
    directory: Path,
    game_info_path: Optional[Path],
    script_extender: bool,
    plugin: tuple[str],
    log_level,
):
    directory = Path(directory)
    start(game, directory, game_info_path, log_level)
    _install(
        game,
        directory,
        game_info_path,
        log_level,
        script_extender,
        list(plugin) if plugin else [],
        plugin_list,
    )
    state.write_state()


@cli.command(help=lang.help_uninstall)
@click_version
@click_help
@click_log_level
@click_opt_game_info
@click_opt_directory
@click_opt_game
def uninstall(game: str, directory: Path, game_info_path: Optional[Path], log_level):
    start(game, directory, game_info_path, log_level)
    _uninstall(game, directory)
    state.write_state(False)


@cli.command(help=lang.help_list)
@click_version
@click_help
@click_log_level
@click_opt_directory
@click_opt_game
def list(game: Optional[str], directory: Optional[Path], log_level):
    start(game, directory, log_level=log_level)
    _list(game, directory)


@cli.command(help=lang.help_pin)
@click_version
@click_help
@click_log_level
@click_arg_directory(required=True)
def pin(directory: Path, log_level):
    start(directory=directory, log_level=log_level)
    _pin(directory, pin=True)


@cli.command(help=lang.help_unpin)
@click_version
@click_help
@click_log_level
@click_arg_directory(required=True)
def unpin(directory: Path, log_level):
    start(directory=directory, log_level=log_level)
    _pin(directory, pin=False)


@cli.command(help=lang.help_update)
@click_version
@click_help
@click_log_level
@click_arg_directory(required=True)
def update(directory: Path, log_level):
    start(directory=directory, log_level=log_level)
    _update(directory)


if __name__ == "__main__":
    cli()
