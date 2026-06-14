#!/usr/bin/env python3

from InquirerPy import prompt
from loguru import logger
from pathlib import Path
from typing import Optional
from util import state_file as state, variables as var

help_install = """Create a new Mod Organizer 2 instance.
\nGAME                            Game for the Mod Organizer 2 instance.
\n                                Options: [{list}]

DIRECTORY                       Path for the Mod Organizer 2 instance."""
help_uninstall = """Uninstall an existing Mod Organizer 2 instance."""
help_list = """List existing Mod Organizer 2 instances."""
help_pin = """Pin the Mod Organizer 2 installation in the specified directory, preventing updates."""
help_unpin = """Unpin the Mod Organizer 2 installation in the specified directory, allowing updates."""
help_update = """Update the Mod Organizer 2 installation in the specified directory, as well as the launch option for the game."""


def list_instances(instance_list: list) -> list:
    """
    Lists instances with their details.

    Parameters
    ----------
    instance_list : list
        List of instances to be displayed.

    Returns
    -------
    list
        List of indices corresponding to the instances.
    """
    instances = [
        f"{idx}: Game: {inst.game}, Path: {inst.instance_path}, Plugins: {', '.join(inst.plugins) if inst.plugins else 'None'}"
        for idx, inst in enumerate(instance_list, start=1)
    ]
    return instances


def prompt_prefix_init() -> bool:
    """
    Prompts the user to confirm their game prefix has been set up.

    Returns
    -------
    bool
        True if the user indicates they have followed the instructions, False otherwise.
    """
    logger.debug(
        f"Prompting user to confirm prefix setup for launcher: {state.current_instance.launcher}"
    )
    if var.unattended:
        logger.debug("Unattended mode: skipping prefix init prompt, defaulting to True")
        return True

    match state.current_instance.launcher:
        case "steam":
            instructions = """Before continuing, please ensure your Steam prefix is set up correctly:

  1. Right-click on the game in your Steam library.
  2. Select 'Properties', and navigate to the 'Compatibility' tab.
  3. Check the box for 'Force the use of a specific Steam Play compatibility tool', if it's not already checked.
  4. From the dropdown menu, select your preferred Proton version. Proton 10.0 is the supported and recommended version.
  5. If you haven't already, launch the game once to allow Steam to set up the prefix, then exit completely.
  6. Do not launch the game again until the installation process is finished."""
        case "gog" | "epic":
            instructions = """Before continuing, please ensure your Heroic prefix is set up correctly:

  1. Right-click on the game in your Heroic library.
  2. Select 'Settings', and navigate to the 'WINE' tab.
  3. Under 'Wine Version', select your preferred Wine/Proton version.
     * Proton - Proton 10.0 is the currently supported and recommended version.
     * If Proton versions are not available, you will need to enable "Allow using Valve Proton builds to run games"
       in Heroic's Settings, under the 'Advanced' tab. Then, ensure that Proton is downloaded and installed in Steam.
  4. Optional: Navigate to the 'OTHER' tab and check 'Use Steam Runtime'. This is recommended and may help with compatibility.
  5. If you haven't already, launch the game once to allow Heroic to set up the prefix, then exit completely.
  6. Do not launch the game again until the installation process is finished."""

    msg = {
        "type": "confirm",
        "message": f"{instructions}\n\n  Have you completed these steps?",
        "name": "prefix_init_done",
        "default": False,
    }
    result = prompt([msg])
    logger.debug(f"User confirmed prefix setup: {result['prefix_init_done']}")
    return result["prefix_init_done"]


def prompt_install_mo2_checksum_fail(mo2_path: str) -> bool:
    """
    Prompts the user when Mod Organizer 2 checksum verification fails.

    Returns
    -------
    bool
        True if the user wants to proceed with installation, False otherwise.
    """
    logger.debug(f"MO2 checksum verification failed for: {mo2_path}")
    if var.unattended:
        logger.debug(
            "Unattended mode: aborting on checksum failure (defaulting to False)"
        )
        return False

    message = f"""Mod Organizer 2 checksum verification has failed for the installation located at: {mo2_path}
  This could indicate that an updated version is available in this installer, or that the installation is corrupted.

  Do you want to proceed with the installation anyway?"""

    msg = {
        "type": "confirm",
        "message": message,
        "name": "mo2_checksum_proceed",
        "default": False,
    }
    result = prompt([msg])
    logger.debug(
        f"User chose to proceed with failed checksum: {result['mo2_checksum_proceed']}"
    )
    return result["mo2_checksum_proceed"]


def prompt_install_scriptextender_choice(script_extenders: dict) -> int:
    """
    Prompts the user to choose a script extender from a list.

    Parameters
    ----------
    script_extenders : dict
        Dictionary of available script extenders to choose from.

    Returns
    -------
    int
        The index of the selected script extender.
    """
    logger.debug(
        f"Prompting user to select script extender from {len(script_extenders)} options"
    )
    if var.unattended:
        logger.debug("Unattended mode: auto-selecting first script extender (index 0)")
        return 0

    message = "Multiple script extenders are available for installation.\n  Please select one: "
    choices = []
    idx = 0
    for se in script_extenders.values():
        idx += 1
        version = getattr(se, "version", "Unknown Version")
        runtimes = getattr(se, "runtime", "N/A")
        runtimes = runtimes.get(var.launcher) if runtimes else None
        runtime = None
        if isinstance(runtimes, dict):
            for key, value in runtimes.items():
                if isinstance(value, list):
                    runtime = ", ".join(value)
                else:
                    runtime = value
        else:
            runtime = runtimes
        choices.append(f"{idx}: Version {version} for runtime: [{runtime}]")

    msg = {
        "type": "list",
        "message": message,
        "choices": choices,
        "name": "scriptextender_choice",
    }
    result = prompt([msg])
    index = int(result["scriptextender_choice"].split(":")[0]) - 1
    logger.debug(f"User selected script extender at index: {index}")
    return index


def prompt_instance_choice(
    message: str = None, instance_list: list = [], additional_choices: list = []
) -> int | str:
    """
    Prompts the user to choose an instance from a list.

    Parameters
    ----------
    message : str
        The message to display in the prompt.
    instance_list : list
        List of instances to choose from.
    additional_choices : list
        Additional choices to include in the prompt.

    Returns
    -------
    int | str
        The index of the selected instance.
    """
    if message is None:
        message = "Select the instance to use: "
    if var.unattended:
        logger.debug("Unattended mode: auto-selecting first instance (index 1)")
        return 1
    choices = list_instances(instance_list) + additional_choices
    msg = {
        "type": "list",
        "message": message,
        "choices": choices,
        "name": "instance_choice",
    }
    result = prompt([msg])
    result = result["instance_choice"].split(":")[0]
    if result.isdigit():
        result = int(result)
    logger.debug(f"User selected instance: {result}")
    return result


def prompt_instance_choice_existing(
    existing_instances: list[state.InstanceData],
) -> Path | str:
    """
    Prompts the user to choose between using an existing instance or creating a new one.
    """
    logger.debug(
        f"Prompting user to select from {len(existing_instances)} existing instances or create new"
    )
    if var.unattended:
        logger.debug("Unattended mode: auto-selecting 'Create new instance'")
        return "Create new instance"

    choices = [
        f"{inst.nexus_slug} at {inst.instance_path}" for inst in existing_instances
    ] + ["Create new instance"]

    msg = {
        "type": "list",
        "message": "Multiple instances found. Choose an option: ",
        "choices": choices,
        "name": "instance_option",
    }
    result = prompt([msg])
    if not result["instance_option"] == "Create new instance":
        result["instance_option"] = Path(result["instance_option"].split(" at ")[1])
    logger.debug(f"User chose: {result['instance_option']}")
    return result["instance_option"]


def prompt_instance_choice_exact() -> bool:
    """
    Prompts the user to confirm using the exact instance found.
    """
    logger.debug("Instance path conflict detected - prompting user for confirmation")
    if var.unattended:
        logger.debug(
            "Unattended mode: defaulting to True (proceed with exact instance path)"
        )
        return True

    message = """The path of the chosen instance directly matches the directory you specified.

  It is not recommended to create an instance where one already exists, as this can lead to conflicts and data loss.
  NO support will be provided for instances created in this way.
  To update the existing instance, please use the 'update' command instead.

  Do you wish to continue?"""

    msg = {
        "type": "confirm",
        "message": message,
        "name": "use_exact_instance",
        "default": True,
    }
    result = prompt([msg])
    logger.debug(
        f"User chose to use exact instance path: {result['use_exact_instance']}"
    )
    return result["use_exact_instance"]


def prompt_instance_conflict() -> bool:
    """
    Prompts the user to confirm proceeding when an instance conflict is detected.
    """
    logger.debug(
        f"Instance link conflict detected for game: {state.current_instance.game}"
    )
    if var.unattended:
        logger.debug(
            "Unattended mode: defaulting to False (do not overwrite existing link)"
        )
        return False

    message = f"""An existing instance link was found for the game {state.current_instance.game}.

    This is primarily used for Nexus' 'Mod Manager Download' button. Overwriting this link will cause the 'Mod Manager Download' button to point to the new instance instead of the old one.

    Would you like to remove the existing link and create a new one pointing to the new instance?"""

    msg = {
        "type": "confirm",
        "message": message,
        "name": "instance_conflict_proceed",
        "default": False,
    }
    result = prompt([msg])
    logger.debug(
        f"User chose to overwrite existing link: {result['instance_conflict_proceed']}"
    )
    return result["instance_conflict_proceed"]


def prompt_launcher_choice(
    steam_path: Optional[str], gog_path: Optional[str], epic_path: Optional[str]
) -> str:
    """
    Prompts the user to choose which launcher to use.
    """
    logger.debug("Prompting user to select launcher")
    choices = []
    if steam_path:
        choices.append(f"Steam: {steam_path}")
    if gog_path:
        choices.append(f"GOG: {gog_path}")
    if epic_path:
        choices.append(f"Epic: {epic_path}")
    if var.unattended:
        logger.debug(f"Unattended mode: auto-selecting first launcher: {choices[0]}")
        return choices[0]

    msg = {
        "type": "list",
        "message": "Select the launcher to use: ",
        "choices": choices,
        "name": "launcher_choice",
    }
    result = prompt([msg])
    logger.debug(f"User selected launcher: {result['launcher_choice']}")
    return result["launcher_choice"]


def prompt_uninstall_choice(instance_list: list) -> int | str:
    """
    Prompts the user to choose which instance to uninstall.
    """
    msg = "Enter index of instance to uninstall (or 'all'): "
    result = prompt_instance_choice(msg, instance_list, ["All"])
    return result


def prompt_uninstall_confirm():
    """
    Prompts the user to confirm uninstallation of the selected instance(s).
    """
    logger.debug("Prompting user to confirm uninstallation")
    if var.unattended:
        logger.debug("Unattended mode: auto-confirming uninstall")
        return True
    msg = {
        "type": "confirm",
        "message": "Are you sure you want to uninstall the selected instance(s)?",
        "name": "confirm_uninstall",
        "default": False,
    }
    result = prompt([msg])
    logger.debug(f"User confirmed uninstallation: {result['confirm_uninstall']}")
    return result["confirm_uninstall"]


def prompt_uninstall_trash() -> bool:
    """
    Prompts the user to choose whether to move files to trash or delete permanently.

    Returns
    -------
    bool
        True if the user chooses to delete permanently, False if moving to trash.
    """
    logger.debug("Prompting user for trash/permanent delete choice")
    if var.unattended:
        logger.debug("Unattended mode: defaulting to Move to Trash (False)")
        return False

    msg = {
        "type": "list",
        "message": "Please choose how to handle the deleted files:",
        "choices": ["Move to Trash", "Delete Permanently"],
        "name": "trash_choice",
        "default": "Move to Trash",
    }
    result = prompt([msg])
    permanent_delete = result["trash_choice"] == "Delete Permanently"
    logger.debug(f"User chose permanent delete: {permanent_delete}")
    if permanent_delete:
        return True
    return False


def prompt_uninstall_trash_confirm() -> bool:
    """
    Prompts the user to confirm permanent deletion.
    """
    logger.debug("Prompting user to confirm permanent deletion")
    if var.unattended:
        logger.debug(
            "Unattended mode: defaulting to False (do not confirm permanent deletion)"
        )
        return False

    msg = {
        "type": "confirm",
        "message": "Are you sure you want to permanently delete this? This action cannot be undone.",
        "name": "confirm_trash_config",
        "default": False,
    }
    result = prompt([msg])
    logger.debug(f"User confirmed permanent deletion: {result['confirm_trash_config']}")
    return result["confirm_trash_config"]
