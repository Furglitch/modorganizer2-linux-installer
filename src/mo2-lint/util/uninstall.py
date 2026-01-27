#!/usr/bin/env python3

from util.state_file import match_instances, remove_instance
from loguru import logger


def uninstall(game=None, directory=None):
    matched = match_instances(game, directory)
    if matched is None:
        logger.error("No instances found to uninstall.")
        return

    length = len(matched)
    choice = []

    print(f"Found {length} matching instance(s) for uninstallation.")

    if length == 1:
        logger.info("Only one instance found. Proceeding to uninstall...")
        choice = matched
    else:
        index = input("\nEnter index of instance to uninstall (or 'all'): ").strip()
        if index.isdigit():
            if not (index.isdigit() and (0 < int(index) < (len(matched) + 1))):
                logger.error("Invalid index. Aborting uninstallation.")
                return
            logger.info(f"Uninstalling instance {index}...")
            choice.append(matched[int(index) - 1])
        elif index.lower() == "all" or index.lower() == "a":
            logger.info("Uninstalling all matching instances...")
            choice = matched
        else:
            logger.error("Invalid input. Aborting uninstallation.")
            return

    confirm_uninstall(choice)


def confirm_uninstall(choice):
    confirm = input(
        "Are you sure you want to uninstall the selected instance(s)? This action cannot be undone. [y/N]: "
    )
    if confirm.lower() == "y":
        for inst in choice:
            remove_instance(inst, ["symlink", "install", "state"])
