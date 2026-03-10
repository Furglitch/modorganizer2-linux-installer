#!/usr/bin/env python3

from loguru import logger
from typing import Union, Optional
import click

try:
    from . import steam, epic
except Exception:
    import steam
    import epic

from util import variables as var


def read_launch_option(
    launcher: str,
    game_id: Union[int, str],
    output: bool = False,
) -> Union[list[var.AppInfo], list[dict]]:
    """
    Read launch options for a game from the appropriate launcher.

    Parameters:
    -----------
    launcher : str
        The launcher type ("steam" or "epic").
    game_id : int | str
        Game identifier (appid for Steam, epic_id for Epic).
    output : bool
        Whether to print the launch options to stdout.

    Returns:
    --------
    list[var.AppInfo] | list[dict]
        Launch options for the specified game.
    """
    if launcher == "steam":
        return steam.read_internal(appid=int(game_id), output=output)
    elif launcher == "epic":
        return epic.read_internal(epic_id=str(game_id), output=output)
    else:
        logger.error(f"Unsupported launcher type: {launcher}")
        return []


def add_launch_option(
    launcher: str,
    game_id: Union[int, str],
    executable: str,
    arguments: list = [],
    label: str = "Launch Mod Organizer",
    opt_type: str = "none",
    oslist: Optional[list[str]] = None,
    osarch: Optional[str] = None,
    no_backup: bool = False,
) -> Optional[int]:
    """
    Add a launch option for a game to the appropriate launcher.

    Parameters:
    -----------
    launcher : str
        The launcher type ("steam" or "epic").
    game_id : int | str
        Game identifier (appid for Steam, epic_id for Epic).
    executable : str
        The executable to launch.
    arguments : list
        Arguments to pass to the executable.
    label : str
        Display name for the launch option.
    opt_type : str
        Type of launch option (Steam only: 'default', 'none', 'vr', 'server').
    oslist : list[str]
        Supported operating systems (Steam only).
    osarch : str
        OS architecture (Steam only).
    no_backup : bool
        Skip creating a backup before modifying.

    Returns:
    --------
    int | bool
        For Steam: returns the launch option index.
        For Epic: returns True on success, False on failure.
    """
    if launcher == "steam":
        return steam.add_internal(
            appid=int(game_id),
            executable=executable,
            arguments=arguments,
            label=label,
            opt_type=opt_type,
            oslist=oslist,
            osarch=osarch,
            no_backup=no_backup,
        )
    elif launcher == "epic":
        result = epic.add_internal(
            epic_id=str(game_id),
            executable=executable,
            arguments=arguments,
            label=label,
            no_backup=no_backup,
        )
        return None if result else False
    else:
        logger.error(f"Unsupported launcher type: {launcher}")
        return False


def remove_launch_option(
    launcher: str,
    game_id: Union[int, str],
    index: Optional[int] = None,
    label: str = "Launch Mod Organizer",
    no_backup: bool = False,
) -> bool:
    """
    Remove a launch option for a game from the appropriate launcher.

    Parameters:
    -----------
    launcher : str
        The launcher type ("steam" or "epic").
    game_id : int | str
        Game identifier (appid for Steam, epic_id for Epic).
    index : int
        Launch option index (Steam only, required for Steam).
    label : str
        Launch option name (Epic only).
    no_backup : bool
        Skip creating a backup before modifying.

    Returns:
    --------
    bool
        True if the launch option was removed successfully, False otherwise.
    """
    if launcher == "steam":
        if index is None:
            logger.error("Steam requires an index to remove a launch option")
            return False
        return steam.remove_internal(
            appid=int(game_id), index=index, no_backup=no_backup
        )
    elif launcher == "epic":
        return epic.remove_internal(
            epic_id=str(game_id), label=label, no_backup=no_backup
        )
    else:
        logger.error(f"Unsupported launcher type: {launcher}")
        return False


# --------- #
# Click CLI #
# --------- #

click_opt_no_backup = click.option(
    "--no-backup",
    is_flag=True,
    default=False,
    help="Do not create a backup before modifying.",
)
click_help = click.help_option("-h", "--help", help="Show this message.")


@click.group()
@click.pass_context
def cli(ctx):
    ctx.ensure_object(dict)


@cli.command(help="Read launch options for a game")
@click_help
@click.option(
    "--launcher",
    "-l",
    type=click.Choice(["steam", "epic"], case_sensitive=False),
    required=True,
    help="Launcher type.",
)
@click.argument("game_id", metavar="GAME_ID")
def read(launcher: str, game_id: str):
    """
    Read launch options for a game.

    GAME_ID: Steam AppID (integer) or Epic game ID (string)
    """
    return read_launch_option(launcher=launcher.lower(), game_id=game_id, output=True)


@cli.command(help="Add a launch option for a game")
@click_help
@click.option(
    "--launcher",
    "-l",
    type=click.Choice(["steam", "epic"], case_sensitive=False),
    required=True,
    help="Launcher type.",
)
@click.argument("game_id", metavar="GAME_ID")
@click.argument("executable", metavar="EXECUTABLE")
@click.option(
    "--label",
    default="Custom Launch Option",
    help="Display name for the launch option.",
)
@click.option(
    "--arguments",
    "-a",
    multiple=True,
    help="Arguments to pass to the executable. Can be specified multiple times.",
)
@click.option(
    "--type",
    "-t",
    "opt_type",
    default="default",
    help="Launch option type (Steam only: 'default', 'none', 'vr', 'server').",
)
@click.option(
    "--oslist",
    "-o",
    multiple=True,
    help="Supported operating systems (Steam only). Can be specified multiple times.",
)
@click.option("--osarch", "-s", help="OS architecture (Steam only, e.g., '32', '64').")
@click_opt_no_backup
def add(
    launcher: str,
    game_id: str,
    executable: str,
    label: str,
    arguments: tuple,
    opt_type: str,
    oslist: tuple,
    osarch: str,
    no_backup: bool,
):
    """
    Add a launch option for a game.

    GAME_ID: Steam AppID (integer) or Epic game ID (string)
    EXECUTABLE: Path to the executable to launch
    """
    result = add_launch_option(
        launcher=launcher.lower(),
        game_id=game_id,
        executable=executable,
        label=label,
        arguments=list(arguments),
        opt_type=opt_type,
        oslist=list(oslist) if oslist else None,
        osarch=osarch,
        no_backup=no_backup,
    )
    if launcher.lower() == "steam" and result is not None:
        print(f"Added launch option with index: {result}")
    elif result is not False:
        print(f"Successfully added launch option: {label}")
    else:
        print("Failed to add launch option")


@cli.command(help="Remove a launch option for a game")
@click_help
@click.option(
    "--launcher",
    "-l",
    type=click.Choice(["steam", "epic"], case_sensitive=False),
    required=True,
    help="Launcher type.",
)
@click.argument("game_id", metavar="GAME_ID")
@click.option(
    "--index",
    "-i",
    type=int,
    help="Launch option index (Steam only, required for Steam).",
)
@click.option(
    "--label", help="Launch option name (Epic only, default: 'Custom Launch Option')."
)
@click_opt_no_backup
def remove(
    launcher: str,
    game_id: str,
    index: Optional[int],
    label: Optional[str],
    no_backup: bool,
):
    """
    Remove a launch option for a game.

    GAME_ID: Steam AppID (integer) or Epic game ID (string)
    """
    if launcher.lower() == "steam" and index is None:
        click.echo("Error: --index is required for Steam", err=True)
        raise SystemExit(1)
    if launcher.lower() == "epic" and label is None:
        label = "Custom Launch Option"

    result = remove_launch_option(
        launcher=launcher.lower(),
        game_id=game_id,
        index=index,
        label=label,
        no_backup=no_backup,
    )
    if result:
        print("Successfully removed launch option")
    else:
        print("Failed to remove launch option")


if __name__ == "__main__":
    cli()
