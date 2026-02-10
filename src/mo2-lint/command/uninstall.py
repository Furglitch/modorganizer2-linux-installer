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
        logger.error(f"No MO2 instance found for game={game}, directory={directory}")
        return

    if length == 1:
        logger.debug(
            f"Found 1 matching Mod Organizer 2 instance for game={game}, directory={directory}"
        )
        choice = matched
    else:
        logger.debug(
            f"Found {length} matching Mod Organizer 2 instances for game={game}, directory={directory}"
        )
        for instance in matched:
            instance_list.append(instance)
        instance = lang.prompt_uninstall_choice(instance_list)
        logger.debug(f"User selected instance for uninstallation: {instance}")
        if isinstance(instance, int):
            if not (0 < instance < (len(matched) + 1)):
                logger.warning(f"Invalid instance number selected: {instance}")
                raise SystemExit(1)
            choice.append(matched[instance - 1])
        elif instance.lower() == "all":
            logger.debug("User selected to uninstall all matching instances.")
            choice = matched
        else:
            logger.critical(f"Invalid selection for uninstallation: {instance}")
            raise SystemExit(1)

    confirm = lang.prompt_uninstall_confirm()
    if confirm:
        logger.debug(
            "User confirmed uninstallation. Proceeding to uninstall selected instances."
        )
        for inst in choice:
            remove_instance(inst, ["symlink", "install", "state"])
            logger.info(f"Uninstalled Mod Organizer 2 instance at {inst.instance_path}")
    else:
        logger.debug("Uninstallation aborted by user.")
        pass
