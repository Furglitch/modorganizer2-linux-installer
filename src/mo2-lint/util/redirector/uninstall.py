#!/usr/bin/env python3

from loguru import logger
from util import state_file as state


def uninstall(instance: "state.InstanceData") -> bool:
    """
    Uninstalls the mo2-redirector.executable from the game's installation directory.

    Parameters
    ----------
    instance : InstanceData
        The instance to uninstall the redirector from.

    Returns
    -------
    bool
        True if the redirector was uninstalled successfully, False otherwise.
    """
    logger.info("Uninstalling redirector.")

    game_install_path = (
        instance.game_path if instance.game_path.is_dir() else instance.game_path.parent
    )

    redirector_path = game_install_path / "mo2-redirector.exe"

    success = False
    if redirector_path.exists():
        redirector_path.unlink()
        logger.success(f"Removed redirector from {redirector_path}")
        success = True
    else:
        logger.debug(f"Redirector not found at {redirector_path}, nothing to remove")

    if success:
        logger.success(f"Redirector uninstalled from {game_install_path}")

    return success
