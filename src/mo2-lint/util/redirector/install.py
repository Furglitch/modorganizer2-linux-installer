#!/usr/bin/env python3

from loguru import logger
import stat
from pathlib import Path
from shutil import copy2
from util import variables as var
from util.internal_file import internal_file
from util.checksum import compare_checksum

redirector_build = internal_file("dist", "redirector.exe")


def create_path_entry():
    """
    Creates the path entry file for the redirector.
    """
    game_install_path = (
        var.game_install_path
        if var.game_install_path.is_dir()
        else var.game_install_path.parent
    )

    redirect_file = game_install_path / "modorganizer2" / "instance_path.txt"
    instance_directory = var.input_params.directory / "ModOrganizer.exe"
    redirect_file.parent.mkdir(parents=True, exist_ok=True)
    with open(redirect_file, "w", encoding="utf-8") as file:
        file.write(str(instance_directory))
    logger.debug(f"Wrote MO2 path '{instance_directory}' to '{redirect_file}'.")


def validate(exec_path: Path) -> bool:
    """
    Validates if the redirector is installed and up to date.

    Parameters
    ----------
    exec_path : Path
        The path to the game's executable.

    Returns
    -------
    bool
        True if the redirector is installed and up to date, False otherwise.
    """

    if not exec_path.exists():
        return False
    if not compare_checksum(redirector_build, exec_path):
        return False
    return True


def install():
    """
    Installs the internal redirector executable to the game's installation directory.
    """

    logger.info("Starting Redirector installation...")

    game_install_path = (
        var.game_install_path
        if var.game_install_path.is_dir()
        else var.game_install_path.parent
    )

    if not (game_install_path / "modorganizer2" / "instance_path.txt").exists():
        logger.debug("Creating path entry for Redirector...")
        create_path_entry()

    exec_path = game_install_path / var.game_info[var.input_params.game].executable
    exec_backup = Path(str(exec_path) + ".bak")

    if validate(exec_path):
        logger.info("Redirector is already installed and up to date.")
        return

    if not exec_backup.exists():
        logger.info(f"Creating backup of original executable at {exec_backup}...")
        copy2(exec_path, exec_backup)

    logger.info(f"Installing Redirector executable to {exec_path}...")
    copy2(redirector_build, exec_path)
    exec_path.chmod(exec_path.stat().st_mode | stat.S_IEXEC)
