#!/usr/bin/env python3

import re
import ssl
import tempfile
from getpass import getuser
from pathlib import Path
from shutil import copy2

import certifi
import click
import yaml
from command.install import install as _install
from command.list import list as _list
from command.pin import pin as _pin
from command.uninstall import uninstall as _uninstall
from command.update import update as _update
from loguru import logger
from packaging.version import Version as version
from pydantic_core import from_json
from util import lang
from util import state_file as state
from util import variables as var
from util.internal_file import internal_file

from shared.logger import add_loggers, remove_loggers

ssl_context = ssl.create_default_context(cafile=certifi.where())


def check_update():
    import requests

    logger.info("Checking for updates.")
    try:
        logger.trace("Fetching latest release info from GitHub API.")
        response = from_json(
            requests.get(
                "https://api.github.com/repos/Furglitch/modorganizer2-linux-installer/releases/latest",
                verify=certifi.where(),
            ).text
        )
        latest = version(response["tag_name"].lstrip("v"))
        current = version(var.version)
        logger.trace(f"Latest version: {latest}, Current version: {current}")
        logger.trace(f"Comparing versions: current={current}, latest={latest}")
        if latest > current:
            logger.warning(
                f"A new version of MO2-LINT is available: {latest}. Please update to the latest version."
            )
            return
    except Exception:
        logger.exception("Failed to check for updates")
        return
    logger.info("No updates available.")


def pull_config():
    """
    Attempts to pull the latest configuration files from GitHub.

    Before that, copies default configuration files from internal storage if not already present.
    """
    logger.info("Pulling latest configuration files from GitHub.")
    settings_path = Path("~/.config/mo2-lint/settings.toml").expanduser()
    if not settings_path.exists():
        try:
            logger.debug(
                f"Settings file does not exist in .config: {settings_path}, copying from internal cfg"
            )
            src = internal_file("cfg", "settings.toml")
            settings_path.parent.mkdir(parents=True, exist_ok=True)
            copy2(src, settings_path)
            logger.trace(f"Copied src={src} to dest={settings_path}")
        except Exception as e:
            logger.exception(
                f"Failed to copy internal settings.toml to .config folder: {e}"
            )
            logger.critical(
                "Failed to set up settings.toml. Please ensure the application has permission to write to ~/.config/mo2-lint/ and try again."
            )
            raise SystemExit(1)
    else:
        logger.trace(f"Settings file already exists: {settings_path}")

    for config in (
        "game_info.yml",
        "resource_info.yml",
        "plugin_info.yml",
        "theme_info.yml",
    ):
        logger.debug(f"Processing config file: {config}")
        config_path = Path("~/.config/mo2-lint/", config).expanduser()
        dest = None
        if not config_path.exists():
            try:
                logger.debug(
                    f"File does not exist in .config: {config_path}, copying from internal cfg"
                )
                src = internal_file("cfg", config)
                dest = config_path
                dest.parent.mkdir(parents=True, exist_ok=True)
                copy2(src, dest)
                logger.trace(f"Copied src={src} to dest={dest}")
            except Exception as e:
                logger.exception(
                    f"Failed to copy internal {config} to .config folder: {e}"
                )
                logger.critical(
                    f"Failed to set up config file {config}. Please ensure the application has permission to write to ~/.config/mo2-lint/ and try again."
                )
                raise SystemExit(1)
        else:
            logger.trace(f"Config file already exists: {config_path}")

        # Check if yml schema version is incompatbile (remote yaml has higher version number than local script)
        remote_raw = f"https://raw.githubusercontent.com/Furglitch/modorganizer2-linux-installer/refs/heads/main/configs/{config}"

        try:
            from urllib.request import Request, urlopen

            from requests import get

            # Check remote schema version
            logger.debug(f"Fetching remote config from GitHub: {remote_raw}")
            response = get(remote_raw, verify=certifi.where())
            remote_yml = yaml.load(response.text, Loader=yaml.SafeLoader)
            remote_schema_version = version(str(remote_yml.get("schema", 0)))
            local_version = version(var.version)
            local_base = version(
                local_version.base_version
            )  # TODO: Remove local_base on full 7.0.0 release
            logger.trace(
                f"Parsed schema parts: current={local_version} (base={local_base}), latest={remote_schema_version}"
            )

            if remote_schema_version > local_base:
                logger.warning(
                    f"There is a new schema version for {config}: {remote_schema_version}. It will not be downloaded to prevent incompatibility issues. Please update MO2-LINT to the latest version to get the new config."
                )
            else:
                config_path.parent.mkdir(parents=True, exist_ok=True)
                req = Request(remote_raw)
                with (
                    urlopen(req, context=ssl_context) as response,
                    open(config_path, "wb") as out_file,
                ):
                    out_file.write(response.read())
        except Exception:
            logger.exception(f"Failed to download config file {config}")

    bin_dir = Path("~/.local/bin").expanduser()
    bin_dir.mkdir(parents=True, exist_ok=True)
    wine2linux_path = bin_dir / "wine2linux"

    if not wine2linux_path.exists():
        try:
            src = internal_file("cfg", "wine2linux")
            copy2(src, wine2linux_path)
            wine2linux_path.chmod(wine2linux_path.stat().st_mode | 0o111)
            logger.debug(f"Installed wine2linux to {wine2linux_path}")
        except Exception as e:
            logger.exception(f"Failed to install wine2linux to {wine2linux_path}: {e}")
            raise SystemExit(1)
    else:
        logger.trace(f"wine2linux already exists: {wine2linux_path}")

    tweaks_file = internal_file("cfg", "tweaks.reg")
    edit_file = Path(tempfile.gettempdir()) / "mo2-lint-tweaks.reg"
    user = getuser()

    try:
        copy2(tweaks_file, edit_file)
        txt = edit_file.read_text()
        if user == "user":
            logger.trace(
                "Executing user is named user; leaving registry tweak paths unchanged"
            )
        else:
            txt = txt.replace("/home/user", f"/home/{user}")
            edit_file.write_text(txt)
            logger.debug(f"Rewrote tweaks.reg for user {user}: {tweaks_file}")
    except Exception as e:
        logger.exception(f"Failed to prepare tweaks.reg at {tweaks_file}: {e}")
        raise SystemExit(1)


game_list = None
plugin_list = None


def pre_init():
    """
    Performs pre-initialization tasks such as loading game and plugin information
    and setting up logging. This is used to prepare help texts and command validation.
    """
    remove_loggers()
    add_loggers(log_level="TRACE", script="mo2-lint", process="pre-check")
    check_update()
    pull_config()  # Temporarily disable for development
    var.load_settings()
    var.load_games_info()
    var.load_resource_info()
    var.load_plugin_info()
    var.load_theme_info()
    global game_list, plugin_list
    game_list = ", ".join(var.games_info.keys())
    plugin_list = ", ".join(var.plugin_info.keys())


pre_init()


def start(
    game: str | None = None,
    directory: Path | str | None = None,
    game_info_path: Path | str | None = None,
    log_level: str | None = "INFO",
    unattended: bool = False,
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

    Returns:
    --------
    tuple[Optional[str], Optional[Path]]
        Depending on the provided parameters, returns the game and/or directory
    """
    remove_loggers()
    add_loggers(log_level=log_level, script="mo2-lint", process="installer")
    logger.debug(f"Starting MO2-LINT with log level: {log_level}")
    var.unattended = unattended
    logger.debug(f"Unattended mode: {unattended}")
    if directory:
        directory = str(directory).rstrip("/")
        directory = Path(directory).expanduser().resolve()
    if game:
        load_games_info(game_info_path)
        if game not in var.games_info:
            available_games = ", ".join(var.games_info.keys())
            logger.critical(
                f"Game '{game}' not supported. Available games: {available_games}"
            )
            raise SystemExit(1)
        var.load_game_info(game)
    state.load_state_file()
    logger.debug(f"Initialization complete. Game: {game}, Directory: {directory}")
    return game or None, directory or None


# Helper Functions
def load_games_info(game_info_path: Path | str | None):
    """
    Loads the standard or custom game information file.

    Parameters:
    -----------
    game_info_path : Path | str, optional
        Path to a custom game_info.yml file.
    """
    if game_info_path:
        game_info_path = Path(game_info_path).expanduser()
        if not game_info_path.exists():
            logger.warning(
                f"Provided game_info.yml path does not exist: {game_info_path}"
            )
            logger.debug("Defaulting to standard game_info.yml from .config folder.")
            var.load_games_info()
        else:
            logger.debug(f"Using custom game_info.yml from path: {game_info_path}")
            var.load_games_info(game_info_path)
    else:
        var.load_games_info()


def load_game_info(game: str | None, game_info_path: Path | str | None):
    """
    Loads game information, both broad and specific to the target game.

    Parameters:
    -----------
    game : str, optional
        The target game for which to load game_info.
    game_info_path : Path | str, optional
        Path to a custom game_info.yml file.
    """
    load_games_info(game_info_path)
    var.load_game_info(game)


click_version = click.version_option(version=var.version, prog_name="mo2-lint")
click_help = click.help_option("-h", "--help", help="Show this message.")
click_log_level = click.option(
    "--log-level",
    "-l",
    "log_level",
    type=click.Choice(["DEBUG", "INFO", "TRACE"], case_sensitive=False),
    default=var.settings.log_level
    if var.settings and var.settings.log_level
    else "INFO",
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
click_opt_theme = click.option(
    "--theme",
    "-t",
    type=click.Choice(["auto", *var.theme_info.keys()], case_sensitive=False),
    default=var.settings.theme if var.settings and var.settings.theme else None,
    help=f"Apply an included MO2 theme during installation.\nOptions: [auto, {', '.join(var.theme_info.keys())}]",
)
click_opt_directory = click.option(
    "--directory",
    "-d",
    type=click.Path(file_okay=False, dir_okay=True),
    help="Target install path for the Mod Organizer 2 instance.",
)
click_unattended = click.option(
    "--unattended",
    "-u",
    is_flag=True,
    default=False,
    help="Run without interactive prompts, using defaults for all choices.",
)


def click_arg_directory(required=False, default=None):
    return click.argument(
        "directory",
        required=required,
        default=default,
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


click_opt_mo2_archive = click.option(
    "--mo2-archive",
    "mo2_archive",
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    default=None,
    help="Install MO2 from a local .zip/.7z archive instead of downloading.",
)
click_opt_mo2_checksum = click.option(
    "--mo2-checksum",
    "mo2_checksum",
    type=str,
    default=None,
    help="SHA-256 checksum of the --mo2-archive file (required with it).",
)


def validate_mo2_archive(mo2_archive: str | None, mo2_checksum: str | None):
    if not mo2_archive:
        return
    if not mo2_checksum:
        logger.critical("--mo2-checksum is required when --mo2-archive is provided.")
        raise SystemExit(1)
    if Path(mo2_archive).suffix.lower() not in (".zip", ".7z"):
        logger.critical(
            f"--mo2-archive must be a .zip or .7z file, but got '{Path(mo2_archive).name}'."
        )
        raise SystemExit(1)


class CustomCommand(click.Command):  # Move [OPTIONS] to the end in the full help text
    class MoveOptions(click.Command):
        def get_help(self, ctx):
            usage = super().get_help(ctx)
            usage = usage.replace(" [OPTIONS]", "", 1)
            m = re.search(r"^(Usage: .+?)\n", usage, flags=re.MULTILINE)
            if m:
                _start, end = m.span(1)
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
@click_unattended
@click_opt_game_info
@click_opt_theme
@click.option(
    "--launcher",
    "-L",
    type=click.Choice(["steam", "gog", "epic"], case_sensitive=False),
    default=var.settings.launcher if var.settings and var.settings.launcher else None,
    help="Force a specific launcher instead of auto-detecting.",
)
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
    default=tuple(var.settings.plugins)
    if var.settings and var.settings.plugins
    else (),
    help="Specify MO2 plugins to download and install.",
)
@click_opt_mo2_archive
@click_opt_mo2_checksum
@click_arg_game(required=True)
@click_arg_directory(required=False)
def install(
    game: str,
    directory: Path | None,
    game_info_path: Path | None,
    launcher: str | None,
    script_extender: bool,
    plugin: tuple[str],
    theme: str | None,
    mo2_archive: str | None,
    mo2_checksum: str | None,
    log_level,
    unattended: bool,
):
    game, directory = start(game, directory, game_info_path, log_level, unattended)
    logger.debug(
        f"Running install command with game={game}, directory={directory}, game_info_path={game_info_path}, launcher={launcher}, script_extender={script_extender}, plugin={plugin}, mo2_archive={mo2_archive}"
    )
    if plugin:
        for p in plugin:
            if p not in var.plugin_info:
                logger.critical(
                    f"Plugin '{p}' not supported. Available plugins: {list(var.plugin_info.keys())}",
                )
                raise SystemExit(1)
    validate_mo2_archive(mo2_archive, mo2_checksum)
    _install(
        game,
        directory,
        game_info_path,
        log_level,
        script_extender,
        plugin,
        theme,
        launcher,
        Path(mo2_archive) if mo2_archive else None,
        mo2_checksum,
    )
    state.write_state()


@cli.command(help=lang.help_uninstall)
@click_version
@click_help
@click_log_level
@click_unattended
@click_opt_game_info
@click_opt_directory
@click_opt_game
def uninstall(
    game: str,
    directory: Path,
    game_info_path: Path | None,
    log_level,
    unattended: bool,
):
    game, directory = start(game, directory, game_info_path, log_level, unattended)
    logger.debug(
        f"Running uninstall command with game={game}, directory={directory}, game_info_path={game_info_path}"
    )
    _uninstall(game, directory)
    state.write_state(False)


@cli.command(help=lang.help_list)
@click_version
@click_help
@click_log_level
@click_unattended
@click_opt_directory
@click_opt_game
def list(game: str | None, directory: Path | None, log_level, unattended: bool):
    game, directory = start(game, directory, log_level=log_level, unattended=unattended)
    logger.debug(f"Running list command with game={game}, directory={directory}")
    _list(game, directory)


@cli.command(help=lang.help_pin)
@click_version
@click_help
@click_log_level
@click_unattended
@click_arg_directory(required=True)
def pin(directory: Path, log_level, unattended: bool):
    _waste, directory = start(
        directory=directory, log_level=log_level, unattended=unattended
    )
    logger.debug(f"Running pin command with directory={directory}")
    _pin(directory, pin=True)


@cli.command(help=lang.help_unpin)
@click_version
@click_help
@click_log_level
@click_unattended
@click_arg_directory(required=True)
def unpin(directory: Path, log_level, unattended: bool):
    _waste, directory = start(
        directory=directory, log_level=log_level, unattended=unattended
    )
    logger.debug(f"Running unpin command with directory={directory}")
    _pin(directory, pin=False)


@cli.command(help=lang.help_update)
@click_version
@click_help
@click_log_level
@click_unattended
@click_opt_game_info
@click_opt_theme
@click_opt_mo2_archive
@click_opt_mo2_checksum
@click_arg_directory(required=True)
def update(
    directory: Path,
    game_info_path: Path | None,
    theme: str | None,
    mo2_archive: str | None,
    mo2_checksum: str | None,
    log_level,
    unattended: bool,
):
    _waste, directory = start(
        directory=directory,
        game_info_path=game_info_path,
        log_level=log_level,
        unattended=unattended,
    )
    logger.debug(
        f"Running update command with directory={directory}, game_info_path={game_info_path}, theme={theme}, mo2_archive={mo2_archive}"
    )
    validate_mo2_archive(mo2_archive, mo2_checksum)
    var.set_parameters(
        {
            "game": "placeholder",
            "directory": directory,
            "game_info_path": game_info_path,
            "log_level": log_level,
            "script_extender": None,
            "theme": theme,
            "plugins": [],
            "mo2_archive": Path(mo2_archive) if mo2_archive else None,
            "mo2_checksum": mo2_checksum,
        }
    )
    _update(
        directory,
        theme,
        Path(mo2_archive) if mo2_archive else None,
        mo2_checksum,
    )


if __name__ == "__main__":
    cli()
