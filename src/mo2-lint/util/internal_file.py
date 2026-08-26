#!/usr/bin/env python3

import sys
from pathlib import Path

from loguru import logger

# Bundle directory names (from the PyInstaller --add-data flags) mapped to their
# equivalents in the source tree, for when the script is run unfrozen.
_SOURCE_LAYOUT = {
    "cfg": "configs",
    "src": "src/mo2-lint",
}


def internal_file(*parts) -> Path:
    """
    Get the path to an internal file within the package.

    Parameters
    ----------
    parts : str
        Relative path components to the internal file. (i.e. `"dist", "file.exe"`)

    Returns
    -------
    Path
        The full path to the internal file's temporary location.
    """

    meipass = getattr(sys, "_MEIPASS", None)
    if meipass is not None:
        path = Path(meipass).joinpath(*parts)
    else:
        # Unfrozen: resolve against the repository root, remapping the bundle
        # directory names onto their source-tree equivalents.
        root = Path(__file__).resolve().parents[3]
        remapped = list(parts)
        if remapped:
            remapped[0] = _SOURCE_LAYOUT.get(remapped[0], remapped[0])
        path = root.joinpath(*remapped)

    logger.trace(f"Accessing internal file: {path}")
    return path
