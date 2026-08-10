#!/usr/bin/env python3

from loguru import logger
from pathlib import Path
from util import variables as var
from util.steam import proton_wrapper


def read_internal(appid: int, output: bool = False) -> list[dict]:
    """
    Read the MO2 Steam Proton wrapper for a specific appid.

    Parameters:
    -----------
    appid : int
        The Steam appid for which to read the wrapper.
    output : bool
        Whether to print the wrapper information to stdout.

    Returns:
    --------
    list[dict]
        A list of launch option dictionaries for the specified Steam appid
    """

    wrapper = proton_wrapper.read(appid)
    if not wrapper:
        return []

    if output:
        print(f"Steam Proton wrapper for appid {appid}:")
        print(f"  Name: {wrapper.display_name}")
        print(f"  Tool ID: {wrapper.tool_id}")
        print(f"  Path: {wrapper.install_path}")
    else:
        logger.trace(f"Steam Proton wrapper for appid {appid}: {wrapper}")

    return [{
        "appid": appid,
        "name": wrapper.display_name,
        "tool_id": wrapper.tool_id,
        "path": wrapper.install_path,
    }]


def get_steam_executable() -> str | None:
    if not var.game_info and not var.game_info.executable:
        return None

    executable = var.game_info.executable
    if isinstance(executable, dict):
        executable = executable.get("steam")

    return executable


def add_internal(
    appid: int,
    executable: str,
    label: str,
) -> bool:
    """
    Install the MO2 Steam Proton compatibility tool wrapper for a game.

    Parameters:
    -----------
    appid : int
        The Steam appid for which to add the wrapper.
    source_executable : str
        The name of the executable (relative to the game dir) that the wrapper
        should intercept and replace with the target_executable. This is
        normally the game's original executable.
    target_executable : str
        The executable to run (relative to the game dir) instead of the
        source_executable. This is normally mo2-redirector.exe.
    label : str
        The display name of the compatability tool.

    Returns:
    --------
    bool
        True if the wrapper was installed successfully, False otherwise
    """

    # XXX: I'm not sure how best to handle the original (source_executable) so
    # look it up here from game_info for now. I'm not a fan of this hidden
    # dependency on var.game_info though.
    game_executable = get_steam_executable()
    if not game_executable:
        logger.error("Could not install Proton wrapper: could not determine the game's original executable.")
        return False

    proton_wrapper.install(
        appid=appid,
        display_name=label,
        source_executable=game_executable,
        target_executable=executable,
    )

    # XXX: reboot steam here?
    # We only need to reboot steam when adding the compatability tool.
    # Steam doesn't cache the inode for the directory, so it's fine to delete
    # and recreate the directory once Steam knows it exists.
    # Also the proton script in the directory can be safely changed without
    # rebooting Steam. So generally the only time you need to restart Steam
    # is when a tool is added, removed, or the details in the vdf files change.

    return True


def remove_internal(appid: int) -> bool:
    """
    Remove the MO2 Steam Proton compatibility tool wrapper for a specific appid.

    Parameters:
    -----------
    appid : int
        The Steam appid for which to remove the wrapper.

    Returns:
    --------
    bool
        True if the wrapper was removed successfully, False otherwise.
    """
    return proton_wrapper.remove(appid)
