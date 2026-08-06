#!/usr/bin/env python3

from dataclasses import dataclass
from loguru import logger
from pathlib import Path
from shutil import rmtree
from stat import S_IXGRP, S_IXOTH, S_IXUSR
from util.internal_file import internal_file
from util.steam.find_library import steam_directories
import os
import shlex


default_proton_path = Path("~/.steam/steam/steamapps/common/Proton 10.0/proton").expanduser()
default_tools_dir = Path("~/.steam/steam/compatibilitytools.d/").expanduser()


@dataclass
class ProtonWrapper:
    """
    Stores information about an installed Steam Proton compatibility tool wrapper.
    """

    tool_id: str
    display_name: str
    install_path: Path


def template_dir() -> Path:
    """
    Gets the bundled Steam Proton wrapper template directory.
    """

    return internal_file("steam-proton-wrapper")


def get_tool_id(appid: int) -> str:
    """
    Gets the compatibility tool ID for a Steam appid.
    """

    return f"mo2_{appid}_redirector"


def get_install_path(appid: int, tools_dir: Path | None = None) -> Path:
    """
    Gets the wrapper install path for a Steam appid.
    """

    return (tools_dir or default_tools_dir) / get_tool_id(appid)


def render(
    source: Path,
    target: Path,
    appid: int,
    display_name: str,
    source_executable: str,
    target_executable: str,
    proton_path: Path | None = None,
) -> ProtonWrapper:
    """
    Renders the bundled Steam Proton wrapper template.

    Parameters:
    -----------
    source : Path
        The source directory containing the template to render.
    target : Path
        The target directory to write the rendered template into. This does not
        delete anything from the target directory (but will overwrite exsiting)
        files.
    appid : int
        The Steam appid for which to add the wrapper.
    display_name : str
        The display name of the compatability tool.
    source_executable : str
        The name of the executable (relative to the game dir) that the wrapper
        should intercept and replace with the target_executable. This is
        normally the game's original executable.
    target_executable : str
        The executable to run (relative to the game dir) instead of the
        source_executable. This is normally mo2-redirector.exe.
    proton_path : Path | None
        The path to a specific proton version to use.
        If None then default_proton_path will be used.
    """

    replacements = {
        "@@TOOL_ID@@": get_tool_id(appid),
        "@@DISPLAY_NAME@@": display_name,
        "@@PROTON_PATH@@": str(proton_path or default_proton_path),
        "@@SOURCE_EXECUTABLE@@": shlex.quote(source_executable),
        "@@TARGET_EXECUTABLE@@": shlex.quote(target_executable),
    }

    target.mkdir(parents=True, exist_ok=True)
    for source_file in source.iterdir():
        if not source_file.is_file():
            continue

        target_file = target / source_file.name
        contents = source_file.read_text(encoding="utf-8")
        for placeholder, value in replacements.items():
            contents = contents.replace(placeholder, value)
        target_file.write_text(contents, encoding="utf-8")

    proton = target / "proton"
    proton.chmod(proton.stat().st_mode | S_IXUSR | S_IXGRP | S_IXOTH)

    return ProtonWrapper(
        tool_id=get_tool_id(appid),
        display_name=display_name,
        install_path=target,
    )


def install(
    appid: int,
    display_name: str,
    source_executable: str,
    target_executable: str,
    source: Path | None = None,
    tools_dir: Path | None = None,
    proton_path: Path | None = None,
) -> ProtonWrapper:
    """
    Installs the MO2 Steam Proton compatibility tool wrapper.
    """

    wrapper = render(
        source=source or template_dir(),
        target=get_install_path(appid, tools_dir),
        appid=appid,
        display_name=display_name,
        source_executable=source_executable,
        target_executable=target_executable,
        proton_path=proton_path,
    )
    logger.info(f"Installed Steam Proton wrapper to {wrapper.install_path}")
    return wrapper


def remove(appid: int, tools_dir: Path | None = None) -> bool:
    """
    Removes the MO2 Steam Proton compatibility tool wrapper.
    """

    path = get_install_path(appid, tools_dir)
    if not path.exists():
        logger.debug(f"Steam Proton wrapper does not exist, skipping removal: {path}")
        return False
    if not path.is_dir():
        logger.warning(f"Steam Proton wrapper path is not a directory: {path}")
        return False

    # XXX: Should we only delete the files we created, and leave the directoy if it's not empty?
    rmtree(path)
    logger.info(f"Removed Steam Proton wrapper at {path}")
    return True


def read(appid: int, tools_dir: Path | None = None) -> ProtonWrapper | None:
    """
    Reads the MO2 Steam Proton compatibility tool wrapper if it exists.
    """

    path = get_install_path(appid, tools_dir)
    if not path.exists():
        return None

    return ProtonWrapper(
        tool_id=get_tool_id(appid),
        display_name=get_tool_id(appid),
        install_path=path,
    )
