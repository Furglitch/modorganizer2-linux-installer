#!/usr/bin/env python3

from util.state_file import match_instances, remove_instance
from loguru import logger


def uninstall(game=None, directory=None):
    def list_instances(list):
        for idx, inst in enumerate(list, start=1):
            print(
                f"    - [{idx}] Game: {inst.game}, Path: {inst.instance_path}, Script Extender: {'Yes' if inst.script_extender else 'No'}, Plugins: {', '.join(inst.plugins) if inst.plugins else 'None'}"
            )

    matched = match_instances(game, directory)
    if matched is None:
        logger.error("No instances found to uninstall.")
        return

    length = len(matched)
    choice = []

    if length == 1:
        logger.info("Only one instance found. Proceeding to uninstall...")
        list_instances(matched)
        choice = matched
    else:
        logger.info(f"Found {length} matching instance(s) for uninstallation.")
        list_instances(matched)
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
        logger.info("Proceeding with uninstallation...")
        for inst in choice:
            logger.info(f"Uninstalling instance at: {inst.instance_path}")
            remove_instance(inst, ["symlink", "install", "state"])
    else:
        logger.info("Uninstallation aborted by user.")
