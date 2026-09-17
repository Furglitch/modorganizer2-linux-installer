#!/usr/bin/env python3


import click
from loguru import logger

try:
    from . import epic, gog, steam
except Exception:
    import epic
    import gog
    import steam

from util import variables as var
from util import state_file as state


def read_launch_option(
    launcher: str,
    game_id: int | str,
    game_path: str | None = None,
    output: bool = False,
) -> list[dict]:
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
    list[dict]
        Launch options for the specified game.
    """
    if launcher == "steam":
        return []
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
    game_id: int | str,
    executable: str,
    arguments: list | None = None,
    label: str = "Launch Mod Organizer",
    game_path: str | None = None,
    proton_wrapper: var.ProtonWrapper | None = None,
    no_backup: bool = False,
) -> bool:
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
    proton_wrapper : ProtonWrapper
        Additional details to setup the Steam Proton wrapper.
    no_backup : bool
        Skip creating a backup before modifying.

    Returns:
    --------
    bool
        returns True on success, False on failure.
    """
    if arguments is None:
        arguments = []
    if launcher == "steam":
        if not proton_wrapper:
            logger.error(
                "Cannot configure Steam Proton wrapper: parameters not defined"
            )
            return False
        return steam.add_internal(
            appid=int(game_id),
            label=label,
            wrapper=proton_wrapper,
            game_executable=state.current_instance.game_executable,
            mo2_executable=executable,
            arguments=arguments,
        )
    elif launcher == "epic":
        return epic.add_internal(
            epic_id=str(game_id),
            executable=executable,
            arguments=arguments,
            label=label,
            no_backup=no_backup,
        )
    elif launcher == "gog":
        from pathlib import Path

        if game_path is None:
            logger.error("GOG requires game_path to be provided")
            return False
        # For GOG, arguments should be a string, not a list
        args_str = " ".join(arguments) if arguments else None
        return gog.add_internal(
            game_path=Path(game_path),
            game_id=str(game_id),
            executable=executable,
            arguments=args_str,
            label=label,
            no_backup=no_backup,
        )
    else:
        logger.error(f"Unsupported launcher type: {launcher}")
        return False


def remove_launch_option(
    launcher: str,
    game_id: int | str,
    label: str = "Launch Mod Organizer",
    game_path: str | None = None,
    proton_wrapper: var.ProtonWrapper | None = None,
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
    label : str
        Launch option name (Epic/GOG only).
    game_path : str
        The game's installation directory (required for GOG).
    proton_wrapper : ProtonWrapper
        Additional parameters for the Steam Proton wrapper that was installed.
    no_backup : bool
        Skip creating a backup before modifying.

    Returns:
    --------
    bool
        True if the launch option was removed successfully, False otherwise.
    """
    if launcher == "steam":
        return steam.remove_internal(appid=int(game_id), wrapper=proton_wrapper)
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
@click_opt_no_backup
def add(
    launcher: str,
    game_id: str,
    executable: str,
    label: str,
    game_path: str,
    arguments: tuple,
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
        no_backup=no_backup,
    )
    if launcher.lower() == "steam" and result is not None:
        print(f"Successfully added compatibility tool: {label}")
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
    "--label",
    help="Launch option name (Required for Epic/GOG).",
)
@click_opt_no_backup
def remove(
    launcher: str,
    game_id: str,
    game_path: str,
    label: str | None,
    no_backup: bool,
):
    """
    Remove a launch option for a game.

    GAME_ID: Steam AppID (integer), Epic game ID (string), or GOG game ID (string)
    """
    if launcher.lower() in ["epic", "gog"] and label is None:
        label = "Custom Launch Option"
    if launcher.lower() == "gog" and not game_path:
        click.echo("Error: --game-path is required for GOG", err=True)
        raise SystemExit(1)

    result = remove_launch_option(
        launcher=launcher.lower(),
        game_id=game_id,
        game_path=game_path,
        label=label,
        no_backup=no_backup,
    )
    if result:
        print("Successfully removed launch option")
    else:
        print("Failed to remove launch option")


if __name__ == "__main__":
    cli()
