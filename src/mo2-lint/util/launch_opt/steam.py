#!/usr/bin/env python3


from loguru import logger
from pathlib import Path
from shutil import copy2
from util import variables as var
from shared.logger import persist_timestamp
import subprocess
import time

try:
    from . import appinfo
except Exception:
    import appinfo

appinfo_vdf = Path("~/.steam/steam/appcache/appinfo.vdf").expanduser()


def backup_vdf(vdf_path: Path) -> Path:
    """
    Backup the appinfo.vdf file by creating a copy with a timestamped filename.

    Parameters:
    -----------
    vdf_path : Path
        The path to the appinfo.vdf file to be backed up.

    Returns:
    --------
    Path
        The path to the created backup file.
    """

    timestamp = persist_timestamp()
    backup_path = vdf_path.with_suffix(f".vdf.{timestamp}.bak")
    copy2(vdf_path, backup_path)
    logger.info(f"Backed up {vdf_path} to {backup_path}")
    return backup_path


def get_next_index(launch_options: var.AppInfo) -> int:
    """
    Get the next available index for a new launch option.

    Parameters:
    -----------
    launch_options
        The existing launch options dictionary from appinfo.vdf.

    Returns:
    --------
    int
        The next available numeric index for a new launch option.
    """
    if not launch_options:
        return 0

    next_index = -1
    for index in launch_options.keys():
        next_index = max(next_index, int(index))
    return next_index + 1


def read_internal(
    vdf: Path = appinfo_vdf, appid: int = None, output: bool = False
) -> list[var.AppInfo]:
    """
    Read the launch options for a specific appid from the appinfo.vdf file.

    Parameters:
    -----------
    vdf : Path
        The path to the appinfo.vdf file. Default is "~/.steam/steam/appcache/appinfo.vdf".
    appid : int
        The Steam appid for which to read the launch options.

    Returns:
    --------
    list[var.AppInfo]
        A list of AppInfo objects representing the launch options for the specified appid.
    """
    if not vdf.exists():
        logger.critical(f"appinfo.vdf not found at {vdf}")
        raise SystemExit(1)

    AppInfo = appinfo.Appinfo
    try:
        data = AppInfo(vdf, choose_apps=True, apps=[appid])
    except appinfo.IncompatibleVDFError as e:
        logger.critical(
            f"Incompatible appinfo.vdf version: {getattr(e, 'vdf_version', e)}"
        )
        raise SystemExit(1)

    app = data.parsedAppInfo.get(appid)
    if not app:
        logger.critical(f"Appid {appid} not found in {vdf}")
        raise SystemExit(1)

    sections = app.get("sections", {})
    appinfo_section = sections.get("appinfo", {})
    config = appinfo_section.get("config", {})
    launch_opts = config["launch"] if "launch" in config else {}

    # print(f"{sections}")
    # print(f"{appinfo_section}")
    # print(f"{config}")
    # print(f"{launch_opts}")

    opts = []
    for key, value in launch_opts.items():
        opts.append(var.AppInfo.from_dict(data=value, index=int(key)))

    if output:
        print(f"Launch options for appid {appid}:")
        for opt in opts:
            # need to add oslist
            print("-" * 64)
            print(f"ID: {opt.index}")
            print(f"  Executable: {opt.executable}")
            print(f"  Arguments: {opt.arguments or '(none)'}")
            print(f"  Description: {opt.description}")
            print(f"  Description (localized): {opt.description_loc or '(none)'}")
            print(f"  Type: {opt.type}")
            print(f"  OS: {opt.oslist or '(none)'}")
            print(f"  OS Architecture: {opt.osarch or '(none)'}")
            print()
    else:
        logger.trace(f"Launch options for appid {appid}: {opts}")

    return opts


def add_internal(
    vdf: Path = appinfo_vdf,
    appid: int = 0,
    executable: Path = None,
    arguments: list = [],
    label: str = "Launch Mod Organizer",
    opt_type: str = "none",
    oslist: list[str] = None,
    osarch: str = None,
    no_backup: bool = False,
) -> int:
    """
    Add a launch option for a specific Steam game ID to the appinfo.vdf file.

    Parameters:
    -----------
    vdf : Path
        The path to the appinfo.vdf file. If None, will search for it.
    appid : int
        The Steam appid for which to add the launch option.
    executable : str
        The executable to launch.
    arguments : list, optional
        Arguments to pass to the executable.
    label : str, optional
        The display name for the launch option. Defaults to "Launch Mod Organizer".
    opt_type : str, optional
        The type of launch option (e.g. "none", "default", "vr", "server", etc.). Defaults to "none".
    oslist : list[str], optional
        The list of operating systems for which the launch option is valid (e.g. ["windows", "linux", "macos"]). Defaults to None (valid for all OSes).
    osarch : str, optional
        The operating system architecture for which the launch option is valid (e.g. "32", "64"). Defaults to None.
    no_backup : bool, optional
        Whether to skip creating a backup of the VDF file. Defaults to False.

    Returns:
    --------
    int
        The index of the newly added launch option.
    """
    opts = read_internal(vdf=vdf, appid=appid)
    AppInfo = appinfo.Appinfo
    try:
        data = AppInfo(vdf, choose_apps=True, apps=[appid])
    except appinfo.IncompatibleVDFError as e:
        logger.critical(
            f"Incompatible appinfo.vdf version: {getattr(e, 'vdf_version', e)}"
        )
        raise SystemExit(1)

    next_index = get_next_index({str(opt.index): opt for opt in opts})
    new_option = var.AppInfo(
        index=next_index,
        executable=str(executable),
        arguments=" ".join(arguments),
        description=label,
        description_loc={"english": label} if label else None,
        type=opt_type,
        oslist=" ".join(oslist) if oslist else None,
        osarch=osarch,
    )
    launch_opts = (
        data.parsedAppInfo.get(appid, {})
        .get("sections", {})
        .get("appinfo", {})
        .get("config", {})
        .get("launch", {})
    )
    launch_opts[str(next_index)] = new_option.to_dict(new_option)

    backup = backup_vdf(vdf) if not no_backup else None
    logger.info(f"Backup created at {backup}" if backup else "No backup created")

    logger.info(f"Adding launch option to appid {appid}")
    logger.debug(f"  ID: {next_index}")
    logger.debug(f"  Executable: {executable}")
    logger.debug(f"  Arguments: {arguments or '(none)'}")
    logger.debug(f"  Description: {label}")
    logger.debug(f"  Type: {opt_type}")
    if osarch:
        logger.debug(f"  OS Architecture: {osarch}")

    data.update_app(appid)
    data.write_data()
    restart_steam()

    return next_index


def remove_internal(
    vdf: Path = appinfo_vdf, appid: int = 0, index: int = -1, no_backup: bool = False
) -> bool:
    """
    Remove a launch option by index for a specific Steam game ID from the appinfo.vdf file.

    Parameters:
    -----------
    vdf : Path
        The path to the appinfo.vdf file. If None, defaults to appinfo_vdf.
    appid : int
        The Steam appid for which to remove the launch option.
    index : int
        The index of the launch option to remove.
    no_backup : bool, optional
        Whether to skip creating a backup of the VDF file. Defaults to False.

    Returns:
    --------
    bool
        True if the launch option was removed successfully, False otherwise.
    """
    read_internal(vdf=vdf, appid=appid)
    AppInfo = appinfo.Appinfo
    try:
        data = AppInfo(vdf, choose_apps=True, apps=[appid])
    except appinfo.IncompatibleVDFError as e:
        logger.critical(
            f"Incompatible appinfo.vdf version: {getattr(e, 'vdf_version', e)}"
        )
        raise SystemExit(1)
    launch_opts = (
        data.parsedAppInfo.get(appid, {})
        .get("sections", {})
        .get("appinfo", {})
        .get("config", {})
        .get("launch", {})
    )
    if str(index) not in launch_opts:
        logger.error(f"Launch option with index {index} not found for appid {appid}")
        return False

    del launch_opts[str(index)]

    backup = backup_vdf(vdf) if not no_backup else None
    logger.info(f"Backup created at {backup}" if backup else "No backup created")

    logger.info(f"Removing launch option with index {index} from appid {appid}")

    data.update_app(appid)
    data.write_data()
    restart_steam()

    return True


def restart_steam():
    """
    Restart Steam and steamwebhelper processes to reload appinfo.vdf changes.
    """
    try:
        if (
            subprocess.run(
                ["pgrep", "-x", "steamwebhelper"], capture_output=True
            ).returncode
            != 0
            or subprocess.run(["pgrep", "-x", "steam"], capture_output=True).returncode
            != 0
        ):
            logger.debug("Steam is not running, no restart needed")
            return
        logger.info("Restarting Steam to apply launch option changes...")
        subprocess.Popen(["killall", "steam", "steamwebhelper"])
        time.sleep(5)  # Wait for processes to terminate
        subprocess.Popen(
            ["steam"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except Exception as e:
        logger.exception(f"Failed to restart Steam: {e}")
        logger.warning(
            "You may need to manually restart Steam for changes to take effect."
        )
