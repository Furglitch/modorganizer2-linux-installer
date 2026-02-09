#!/usr/bin/env python3

from loguru import logger
from util.state_file import match_instances, remove_instance
from util import lang


def uninstall(game=None, directory=None):
    """
    Matches existing instances based on game and/or directory, prompts the user to select which to uninstall, and proceeds with uninstallation after confirmation.

    Parameters
    ----------
    game : str
        The game nexus slug to match.
    directory : str
        The instance directory to match.
    """

    instance_list = []

    matched = match_instances(game, directory)
    length = len(matched)
    choice = []

    if not length or length == 0:
        logger.error("No matching instances found for uninstallation.")
        return

    if length == 1:
        logger.info("Only one instance found. Proceeding to uninstall...")
        logger.info(f"Uninstalling instance at: {matched[0].instance_path}")
        choice = matched
    else:
        for instance in matched:
            instance_list.append(instance)
        logger.info(f"Found {length} matching instance(s) for uninstallation.")
        instance = lang.prompt_uninstall_choice(instance_list)
        if isinstance(instance, int):
            if not (0 < instance < (len(matched) + 1)):
                logger.error("Invalid index. Aborting uninstallation.")
                return
            logger.info(f"Uninstalling instance {instance}...")
            choice.append(matched[instance - 1])
        elif instance.lower() == "all":
            logger.info("Uninstalling all matching instances...")
            choice = matched
        else:
            logger.error("Invalid input. Aborting uninstallation.")
            return

    confirm_uninstall(choice)


def confirm_uninstall(choice):
    """
    Prompts the user for confirmation before uninstalling instances.

    Parameters
    ----------
    choice : dict[int, Instance]
        The instances selected for uninstallation.
    """
    confirm = lang.prompt_uninstall_confirm()
    if confirm:
        logger.info("Proceeding with uninstallation...")
        for inst in choice:
            logger.info(f"Uninstalling instance at: {inst.instance_path}")
            remove_instance(inst, ["symlink", "install", "state"])
    else:
        logger.info("Uninstallation aborted by user.")
