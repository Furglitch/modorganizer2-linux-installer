#!/usr/bin/env python3

import click
from pydantic_core import from_json
from pathlib import Path


def preloadGameInfo():
    filepath = Path(__file__).resolve().parents[2] / "configs" / "game-info.json"
    with open(filepath, "r", encoding="utf-8") as file:
        json = from_json(file.read())
    return list(json.keys())


@click.command()
@click.version_option(version="1.0.0", prog_name="mo2-lint")
@click.help_option("-h", "--help")
@click.argument(
    "game", type=click.Choice(preloadGameInfo(), case_sensitive=False), required=True
)
@click.argument(
    "directory",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    required=True,
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
def main(game, directory, script_extender, plugin):
    """A tool to install and manage Mod Organizer 2 instances."""
    click.echo(f"You have selected the game: {game}")
    click.echo(f"Target directory: {directory}")


if __name__ == "__main__":
    main()
