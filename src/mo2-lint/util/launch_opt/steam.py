#!/usr/bin/env python3


import subprocess
import time

from loguru import logger
from util import variables as var

from util.steam import proton_wrapper


def add_internal(
    appid: int,
    label: str,
    wrapper: var.ProtonWrapper,
    game_executable: str,
    mo2_executable: str,
    arguments: list[str] | None = None,
) -> int:
    """
    Add a compatibility tool for a specific Steam game ID to compatibilitytools.d.

    Parameters:
    -----------
    appid : int
        The Steam appid for which to add the compatibility tool.
    label : str
        The display name for the Steam compatibility tool.
    wrapper : ProtonWrapper
        Parameters for the Steam Proton wrapper.
    executable : str
        The executable to launch.
    arguments : list, optional
        Arguments to pass to the executable.

    Returns:
    --------
    bool
        True if the compatibility tool was added successfully, False otherwise.
    """

    # TODO: Instead of using a fixed default proton version, consider parsing the application files similar to protontricks to locate which compatibility tool the app has been configured to use. Every app should have an explicit tool set as part of the initial setup steps.

    logger.info(f"Adding Steam compatibility tool for appid {appid}")
    logger.debug(f"  Name: {label}")
    logger.debug(f"  Compatibility Tool ID: {wrapper.tool_id}")
    logger.debug(f"  Compatibility Tool Path: {wrapper.tool_path}")
    logger.debug(f"  Proton Version: {wrapper.proton_version}")
    logger.debug(f"  Proton Path: {wrapper.proton_path}")
    logger.debug(f"  Game Executable: {game_executable}")
    logger.debug(f"  MO2 Executable: {mo2_executable}")
    logger.debug(f"  Arguments: {arguments or '(none)'}")

    success = proton_wrapper.install(
        appid=appid,
        display_name=label,
        wrapper=wrapper,
        source_executable=game_executable,
        target_executable=mo2_executable,
    )

    if success:
        restart_steam()
        logger.success(f"Successfully added Steam compatibility tool for appid {appid}")

    return success


def remove_internal(appid: int, wrapper: var.ProtonWrapper | None) -> bool:
    """
    Remove a compatibility tool by index for a specific Steam game ID from the appinfo.vdf file.

    Parameters:
    -----------
    appid : int
        The Steam appid for which to remove the compatibility tool.
    wrapper : ProtonWrapper
        Parameters for the Steam Proton wrapper that was installed.

    Returns:
    --------
    bool
        True if the compatibility tool was removed successfully, False otherwise.
    """

    if not wrapper:
        logger.warning("Steam Proton wrapper not set, trying to resolve")
        wrapper = proton_wrapper.resolve(appid)
        if not wrapper:
            logger.error("Could not resolve Steam Proton wrapper")
            return False

    removed = proton_wrapper.remove(wrapper.tool_path)
    if removed:
        restart_steam()

    return removed


def restart_steam():
    """
    Restart Steam and steamwebhelper processes to reload appinfo.vdf changes.
    """
    try:
        if (
            subprocess.run(
                ["pgrep", "-x", "steamwebhelper"], capture_output=True, check=False
            ).returncode
            != 0
            or subprocess.run(
                ["pgrep", "-x", "steam"], capture_output=True, check=False
            ).returncode
            != 0
        ):
            logger.debug("Steam is not running, no restart needed")
            return
        logger.info("Restarting Steam to apply compatibility tool changes...")
        subprocess.Popen(["killall", "steam", "steamwebhelper"])

        for _ in range(30):  # Wait 30s for processes to terminate
            if (
                subprocess.run(
                    ["pgrep", "-x", "steamwebhelper"], capture_output=True, check=False
                ).returncode
                != 0
                and subprocess.run(
                    ["pgrep", "-x", "steam"], capture_output=True, check=False
                ).returncode
                != 0
            ):
                break
            time.sleep(1)
        else:
            logger.warning(
                "Timed out waiting for Steam to terminate, proceeding anyway..."
            )
        subprocess.Popen(
            ["steam", "-silent"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except Exception:
        logger.exception("Failed to restart Steam")
        logger.warning(
            "You may need to manually restart Steam for changes to take effect."
        )
