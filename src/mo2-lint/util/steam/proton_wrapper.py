#!/usr/bin/env python3

import shlex
from pathlib import Path
from shutil import rmtree
from stat import S_IXGRP, S_IXOTH, S_IXUSR

from loguru import logger

from util import variables as var
from util.internal_file import internal_file
from util.steam.find_library import get_libraries
from util.steam.path import find_steam_root
from util.steam.proton import find_proton, read_require_tool_appid


default_proton_version = "Proton 10.0"

# Use a magic marker file to track that a directory is a proton wrapper managed by our application. We do not want to accidentally delete someone's home directory because of a corrupted state file.
marker_name = ".mo2-lint-proton-wrapper"


def default_template_dir() -> Path:
    """
    Gets the bundled Steam Proton wrapper template directory.
    """
    return internal_file("steam-proton-wrapper")


def format_tool_id(appid: int) -> str:
    """
    Gets the compatibility tool ID for a Steam appid.
    """
    return f"mo2_{appid}_redirector"


def resolve_tool_path(appid: int, tools_dir: Path | None = None) -> Path | None:
    """
    Gets the compatibilitytool.d path for the Proton wrapper.

    Parameters:
    -----------
    appid : int
        The Steam appid the Proton wrapper belongs to.
    tools_dir : Path
        The compatibilitytools.d directory to use.
        If None it will use the default <steam root>/compatibilitytools.d
    """

    if tools_dir is None:
        root = find_steam_root()
        if not root:
            logger.error("Could not find Steam root")
            return None
        tools_dir = root / "compatibilitytools.d"
    return tools_dir / format_tool_id(appid)


def is_proton_wrapper(path: Path) -> bool:
    return (path / marker_name).exists()


def resolve(appid: int, proton_version: str | None = None) -> var.ProtonWrapper | None:
    """
    Resolves values required to install the Steam Proton wrapper.

    Parameters:
    appid : int
        The Steam appid the Proton wrapper belongs to.
    proton_version : str
        The proton version to look for (matches the directory name) for example "Proton 10.0".
        If None the default Proton version will be used.
    """

    if not appid:
        # Should not happen for a Steam game, but the Steam launcher id is defined as int | None.
        # So just in case, bail early oherwise strange things will happen.
        logger.error("Could not resolve Steam Proton wrapper: no appid")
        return None

    if not proton_version:
        proton_version = default_proton_version

    libraries = get_libraries()
    if not libraries:
        logger.error(
            f'Could not find path for Proton "{proton_version}": no library paths found'
        )
        return None

    proton_path = find_proton(libraries, proton_version)
    if not proton_path:
        logger.error(f'Could not find path for Proton "{proton_version}"')
        return None

    logger.debug(f'Found Proton "{proton_version}" at "{proton_path}"')

    tool_path = resolve_tool_path(appid)
    if not tool_path:
        return None

    return var.ProtonWrapper(
        tool_id=format_tool_id(appid),
        tool_path=tool_path,
        proton_version=proton_version,
        proton_path=proton_path,
        pinned=False,
    )


def render(
    source: Path,
    target: Path,
    tool_id: str,
    display_name: str,
    source_executable: str,
    target_executable: str,
    proton_version: str,
    proton_path: Path,
):
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
    tool_id : int
        The compatibility tool ID for a Steam appid.
    display_name : str
        The display name of the compatibility tool.
    source_executable : str
        The name of the executable (relative to the game dir) that the wrapper
        should intercept and replace with the target_executable. This is
        normally the game's original executable.
    target_executable : str
        The executable to run (relative to the game dir) instead of the
        source_executable. This is normally mo2-redirector.exe.
    proton_version : str
        The proton version to look for (matches the directory name) for example "Proton 10.0"
    """

    require_tool_appid = read_require_tool_appid(proton_path)
    if not require_tool_appid:
        logger.warning(
            f'Proton "{proton_version}" require_tool_appid not found. If Proton requires a specific Steam Runtime then it might fail to launch'
        )

    marker = target / marker_name
    replacements = {
        "@@TOOL_ID@@": str(tool_id),
        "@@DISPLAY_NAME@@": str(display_name),
        "@@PROTON_VERSION@@": str(proton_version),
        "@@PROTON_PATH@@": str(proton_path),
        "@@REQUIRE_TOOL_APPID@@": str(require_tool_appid or ""),
        "@@SOURCE_EXECUTABLE@@": shlex.quote(str(source_executable)),
        "@@TARGET_EXECUTABLE@@": shlex.quote(str(target_executable)),
    }

    target.mkdir(parents=True, exist_ok=True)
    marker.touch()

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


def install(
    appid: int,
    display_name: str,
    wrapper: var.ProtonWrapper,
    source_executable: str,
    target_executable: str,
    template_dir: Path | None = None,
) -> bool:
    """
    Installs the MO2 Steam Proton compatibility tool wrapper.

    Parameters:
    -----------
    display_name : str
        The display name of the compatibility tool.
    """

    source = template_dir or default_template_dir()
    target = wrapper.tool_path

    if target.exists() and not is_proton_wrapper(target):
        logger.error(
            f"Not installing Steam Proton wrapper: marker file {marker_name} not found in {target}"
        )
        return False

    render(
        source=source,
        target=target,
        tool_id=wrapper.tool_id,
        display_name=display_name,
        source_executable=source_executable,
        target_executable=target_executable,
        proton_version=wrapper.proton_version,
        proton_path=wrapper.proton_path,
    )

    logger.info(f"Installed Steam Proton wrapper to {target}")
    return True


def remove(path: Path) -> bool:
    """
    Removes the MO2 Steam Proton compatibility tool wrapper.
    """

    if not path:
        # This shouldn't be true, but this is loaded from state no even though
        # path should not be None, that's only a suggestion in Python.
        logger.error("Steam Proton wrapper path missing, skipping removal")
        return False

    if not path.exists():
        logger.debug("Steam Proton wrapper does not exist, skipping removal")
        return False

    if not is_proton_wrapper(path):
        logger.error(
            f"Not removing Steam Proton wrapper directory: marker file {marker_name} not found in {path}"
        )
        return False

    rmtree(path)
    logger.info(f'Removed Steam Proton wrapper at "{path}"')
    return True
