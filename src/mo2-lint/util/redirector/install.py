#!/usr/bin/env python3

from loguru import logger
from pathlib import Path
from shutil import copy2
from util import variables as var, state_file as state
from util.checksum import compare_checksum
from util.internal_file import internal_file
import stat

redirector_build = internal_file("dist", "mo2-redirector.exe")


def validate(redirector_path: Path) -> bool:
    """
    Validates if the redirector is installed and up to date.

    Parameters
    ----------
    redirector_path : Path
        The path to the redirector executable.

    Returns
    -------
    bool
        True if the redirector is installed and up to date, False otherwise.
    """

    if not redirector_path.exists():
        return False
    if not compare_checksum(redirector_build, redirector_path):
        return False
    return True


def install():
    """
    Installs the redirector executable to the game's installation directory.
    """

    logger.info("Installing redirector.")
    game_install_path = (
        state.current_instance.game_path
        if state.current_instance.game_path.is_dir()
        else state.current_instance.game_path.parent
    )

    subdirectory = (
        var.game_info.subdirectory
        if isinstance(var.game_info.subdirectory, str)
        else var.game_info.subdirectory.get(state.current_instance.launcher)
    )
    if game_install_path.name != subdirectory:
        game_install_path = game_install_path.parent / subdirectory
        state.current_instance.game_path = game_install_path

    redirector_path = game_install_path / "mo2-redirector.exe"

    if validate(redirector_path):
        logger.info(
            f"Redirector is already installed and up to date at {redirector_path}"
        )
        return

    logger.debug(f"Game install path: {game_install_path}")
    logger.info(f"Installing redirector to: {redirector_path}")

    copy2(redirector_build, redirector_path)
    redirector_path.chmod(redirector_path.stat().st_mode | stat.S_IEXEC)
    logger.success(f"Redirector installed to {redirector_path}")
