#!/usr/bin/env python3

from loguru import logger
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from util.state_file import InstanceData


def get_game_install_path(instance: "InstanceData") -> Path:
    """
    Get the game installation path for an instance.

    Parameters
    ----------
    instance : InstanceData
        The instance to get the game install path for.

    Returns
    -------
    Path
        The game installation directory path.
    """
    return (
        instance.game_path if instance.game_path.is_dir() else instance.game_path.parent
    )


def get_mo2_symlink_path(instance: "InstanceData") -> Path:
    """
    Get the path where the ModOrganizer.exe symlink should be created.

    Parameters
    ----------
    instance : InstanceData
        The instance to get the symlink path for.

    Returns
    -------
    Path
        The path where the ModOrganizer.exe symlink should exist.
    """
    game_install_path = get_game_install_path(instance)
    return game_install_path / "ModOrganizer.exe"


def create_mo2_symlink(instance: "InstanceData") -> Path:
    """
    Create a symlink from the instance's ModOrganizer.exe to the game install folder.

    Parameters
    ----------
    instance : InstanceData
        The instance to create the symlink for.

    Returns
    -------
    Path
        The path to the created symlink.
    """
    mo2_exe = instance.instance_path / "ModOrganizer.exe"
    symlink_path = get_mo2_symlink_path(instance)

    # Remove existing symlink or file if present
    if symlink_path.exists() or symlink_path.is_symlink():
        symlink_path.unlink()
        logger.trace(f"Removed existing symlink at {symlink_path}")

    # Create the symlink
    symlink_path.symlink_to(mo2_exe)
    logger.info(f"Created symlink from {mo2_exe} to {symlink_path}")

    return symlink_path


def remove_mo2_symlink(instance: "InstanceData") -> bool:
    """
    Remove the ModOrganizer.exe symlink from the game install folder.

    Parameters
    ----------
    instance : InstanceData
        The instance to remove the symlink for.

    Returns
    -------
    bool
        True if the symlink was removed, False if it didn't exist.
    """
    symlink_path = get_mo2_symlink_path(instance)

    if symlink_path.exists() or symlink_path.is_symlink():
        symlink_path.unlink()
        logger.success(f"Removed ModOrganizer.exe symlink from: {symlink_path.parent}")
        return True
    else:
        logger.trace(f"No symlink found at {symlink_path}, nothing to remove")
        return False
