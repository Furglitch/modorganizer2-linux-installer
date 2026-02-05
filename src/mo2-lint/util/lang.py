#!/usr/bin/env python3

from InquirerPy import prompt
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
help_update = """Update the Mod Organizer 2 installation in the specified directory, as well as the redirector for the game."""

prompt_archive_done = """Your prefix has been archived and can be found at: {directory}

Personal data from the archived prefix (e.g. saved games) has been preserved and restored to the new prefix.
Feel free to delete the archive if you no longer need it after confirming your data is intact."""


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
        f"{idx}: Game: {inst.nexus_slug}, Path: {inst.instance_path}, Script Extender: {'Yes' if inst.script_extender else 'No'}, Plugins: {', '.join(inst.plugins) if inst.plugins else 'None'}"
        for idx, inst in enumerate(instance_list, start=1)
    ]
    print(instances)
    return instances


def prompt_archive() -> bool:
    """
    Prompts the user to archive the existing game prefix and create a clean one.

    Returns
    -------
    bool
        True if the user agrees to archive prefix, False otherwise.
    """

    message = """It is recommended to archive your existing game prefix and create a clean one for Mod Organizer 2 to avoid potential conflicts.

  This process will maintain your personal data (save games, settings) while providing a fresh environment for proton-/winetricks to set up the necessary dependencies.
  The archived prefix will be renamed with a timestamp suffix for easy identification.

  Do you want to proceed with archiving the existing prefix and creating a clean one?"""

    msg = {
        "type": "confirm",
        "message": message,
        "name": "archive_clean",
        "default": False,
    }
    result = prompt([msg])
    return result["archive_clean"]


def prompt_archive_init() -> bool:
    """
    Prompts the user to initialize a clean prefix

    Returns
    -------
    bool
        True if the user indicates they have followed the instructions, False otherwise.
    """

    match state.current_instance.launcher:
        case "steam":
            instructions = """To create a clean Steam prefix, please follow these steps:

  1. Right-click on the game in your Steam library.
  2. Select 'Properties', and navigate to the 'Compatibility' tab.
  3. Check the box for 'Force the use of a specific Steam Play compatibility tool', if it's not already checked.
  4. From the dropdown menu, select your preferred Proton version. Proton 10.0 is the supported and recommended version.
  5. Close the properties window and launch the game once to allow Steam to set up the prefix.
  6. Exit the game completely. Do not launch it until the installation process is finished."""
        case "gog" | "epic":
            instructions = """To create a clean prefix for GOG/Epic via Heroic, please follow these steps:

  1. Right-click on the game in your Heroic library.
  2. Select 'Settings', and navigate to the 'WINE' tab.
  3. Under 'Wine Version', select your preferred Wine/Proton version.
     * Proton - Proton 10.0 is the currently supported and recommended version.
     * If Proton versions are not available, you will need to enable "Allow using Valve Proton builds to run games"
       in Heroic's Settings, under the 'Advanced' tab. Then, ensure that Proton is downloaded and installed in Steam.
  4. Optional: Navigate to the 'OTHER' tab and check 'Use Steam Runtime'. This is recommended and may help with compatibility.
  5. Launch the game once to allow Heroic to set up the prefix.
  6. Exit the game completely. Do not launch it until the installation process is finished."""

    msg = {
        "type": "confirm",
        "message": f"{instructions}\n\nHave you completed these instructions?",
        "name": "clean_prefix_done",
        "default": False,
    }
    result = prompt([msg])
    return result["clean_prefix_done"]


def prompt_install_mo2_checksum_fail(mo2_path: str) -> bool:
    """
    Prompts the user when Mod Organizer 2 checksum verification fails.

    Returns
    -------
    bool
        True if the user wants to proceed with installation, False otherwise.
    """

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

    message = "Multiple script extenders are available for installation.\n  Please select one: "
    choices = []
    for se in script_extenders.values():
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
        choices.append(f"{se.name} (Version: {version}, Runtime: [{runtime})]")

    msg = {
        "type": "list",
        "message": message,
        "choices": choices,
        "name": "scriptextender_choice",
    }
    result = prompt([msg])
    return result["scriptextender_choice"]


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
    return result


def prompt_instance_choice_existing():
    """
    Prompts the user to choose between using an existing instance or creating a new one.
    """
    msg = {
        "type": "list",
        "message": "Multiple instances found. Choose an option: ",
        "choices": ["Use existing instance", "Create new instance"],
        "name": "instance_option",
    }
    result = prompt([msg])
    return result["instance_option"]


def prompt_launcher_choice(
    steam_path: Optional[str], gog_path: Optional[str], epic_path: Optional[str]
) -> str:
    """
    Prompts the user to choose which launcher to use.
    """
    choices = []
    if steam_path:
        choices.append(f"Steam: {steam_path}")
    if gog_path:
        choices.append(f"GOG: {gog_path}")
    if epic_path:
        choices.append(f"Epic: {epic_path}")

    msg = {
        "type": "list",
        "message": "Select the launcher to use: ",
        "choices": choices,
        "name": "launcher_choice",
    }
    result = prompt([msg])
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
    msg = {
        "type": "confirm",
        "message": "Are you sure you want to uninstall the selected instance(s)?",
        "name": "confirm_uninstall",
        "default": False,
    }
    result = prompt([msg])
    return result["confirm_uninstall"]


def prompt_uninstall_trash():
    """
    Prompts the user to choose whether to move files to trash or delete permanently.
    """

    msg = {
        "type": "choice",
        "message": "Please choose how to handle the deleted files:",
        "choices": ["Move to Trash", "Delete Permanently"],
        "name": "trash_choice",
        "default": "Move to Trash",
    }
    result = prompt([msg])
    if not result["trash_choice"] == "Move to Trash":
        result["trash_choice"] = True
    else:
        result["trash_choice"] = False
    return result["trash_choice"]
