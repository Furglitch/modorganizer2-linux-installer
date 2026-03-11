#!/usr/bin/env python3

from loguru import logger
from typing import Union, Optional
import click

try:
    from . import steam, epic, gog
except Exception:
    import steam
    import epic
    import gog

from util import variables as var


def read_launch_option(
    launcher: str,
    game_id: Union[int, str],
    game_path: str = None,
    output: bool = False,
) -> Union[list[var.AppInfo], list[dict]]:
    """
    Read launch options for a game from the appropriate launcher.

    Parameters:
    -----------
    launcher : str
        The launcher type ("steam", "epic", or "gog").
    game_id : int | str
        Game identifier (appid for Steam, epic_id for Epic, game_id for GOG).
    game_path : str
        The game's installation directory (required for GOG).
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
    elif launcher == "gog":
        from pathlib import Path

        return gog.read_internal(
            game_path=Path(game_path), game_id=str(game_id), output=output
        )
    else:
        logger.error(f"Unsupported launcher type: {launcher}")
        return []


def add_launch_option(
    launcher: str,
    game_id: Union[int, str],
    executable: str,
    arguments: list = [],
    label: str = "Launch Mod Organizer",
    game_path: str = None,
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
        The launcher type ("steam", "epic", or "gog").
    game_id : int | str
        Game identifier (appid for Steam, epic_id for Epic, game_id for GOG).
    executable : str
        The executable to launch.
    arguments : list
        Arguments to pass to the executable.
    label : str
        Display name for the launch option.
    game_path : str
        The game's installation directory (required for GOG).
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
        For Epic/GOG: returns True on success, False on failure.
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
    elif launcher == "gog":
        from pathlib import Path

        if game_path is None:
            logger.error("GOG requires game_path to be provided")
            return False
        # For GOG, arguments should be a string, not a list
        args_str = " ".join(arguments) if arguments else None
        result = gog.add_internal(
            game_path=Path(game_path),
            game_id=str(game_id),
            executable=executable,
            arguments=args_str,
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
    game_path: str = None,
    no_backup: bool = False,
) -> bool:
    """
    Remove a launch option for a game from the appropriate launcher.

    Parameters:
    -----------
    launcher : str
        The launcher type ("steam", "epic", or "gog").
    game_id : int | str
        Game identifier (appid for Steam, epic_id for Epic, game_id for GOG).
    index : int
        Launch option index (Steam only, required for Steam).
    label : str
        Launch option name (Epic/GOG only).
    game_path : str
        The game's installation directory (required for GOG).
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
    elif launcher == "gog":
        from pathlib import Path

        if game_path is None:
            logger.error("GOG requires game_path to be provided")
            return False
        return gog.remove_internal(
            game_path=Path(game_path),
            game_id=str(game_id),
            label=label,
            no_backup=no_backup,
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
    type=click.Choice(["steam", "epic", "gog"], case_sensitive=False),
    required=True,
    help="Launcher type.",
)
@click.argument("game_id", metavar="GAME_ID")
@click.option(
    "--game-path",
    "-p",
    help="Game installation directory (required for GOG).",
)
def read(launcher: str, game_id: str, game_path: str):
    """
    Read launch options for a game.

    GAME_ID: Steam AppID (integer), Epic game ID (string), or GOG game ID (string)
    """
    if launcher.lower() == "gog" and not game_path:
        click.echo("Error: --game-path is required for GOG", err=True)
        raise SystemExit(1)
    return read_launch_option(
        launcher=launcher.lower(), game_id=game_id, game_path=game_path, output=True
    )


@cli.command(help="Add a launch option for a game")
@click_help
@click.option(
    "--launcher",
    "-l",
    type=click.Choice(["steam", "epic", "gog"], case_sensitive=False),
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
    "--game-path",
    "-p",
    help="Game installation directory (required for GOG).",
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
    game_path: str,
    arguments: tuple,
    opt_type: str,
    oslist: tuple,
    osarch: str,
    no_backup: bool,
):
    """
    Add a launch option for a game.

    GAME_ID: Steam AppID (integer), Epic game ID (string), or GOG game ID (string)
    EXECUTABLE: Path to the executable to launch
    """
    if launcher.lower() == "gog" and not game_path:
        click.echo("Error: --game-path is required for GOG", err=True)
        raise SystemExit(1)
    result = add_launch_option(
        launcher=launcher.lower(),
        game_id=game_id,
        executable=executable,
        label=label,
        game_path=game_path,
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
    type=click.Choice(["steam", "epic", "gog"], case_sensitive=False),
    required=True,
    help="Launcher type.",
)
@click.argument("game_id", metavar="GAME_ID")
@click.option(
    "--game-path",
    "-p",
    help="Game installation directory (required for GOG).",
)
@click.option(
    "--index",
    "-i",
    type=int,
    help="Launch option index (Required for Steam).",
)
@click.option(
    "--label",
    help="Launch option name (Required for Epic/GOG).",
)
@click_opt_no_backup
def remove(
    launcher: str,
    game_id: str,
    game_path: str,
    index: Optional[int],
    label: Optional[str],
    no_backup: bool,
):
    """
    Remove a launch option for a game.

    GAME_ID: Steam AppID (integer), Epic game ID (string), or GOG game ID (string)
    """
    if launcher.lower() == "steam" and index is None:
        click.echo("Error: --index is required for Steam", err=True)
        raise SystemExit(1)
    if launcher.lower() in ["epic", "gog"] and label is None:
        label = "Custom Launch Option"
    if launcher.lower() == "gog" and not game_path:
        click.echo("Error: --game-path is required for GOG", err=True)
        raise SystemExit(1)

    result = remove_launch_option(
        launcher=launcher.lower(),
        game_id=game_id,
        game_path=game_path,
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
