#!/usr/bin/env python3

from loguru import logger
from pathlib import Path
import sys


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

    path = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve()))
    logger.trace(f"Accessing internal file: {path.joinpath(*parts)}")
    return path.joinpath(*parts)
