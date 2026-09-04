#!/usr/bin/env python3

import sys
from pathlib import Path

from loguru import logger


def internal_file(*parts) -> Path:
    """
    Resolves the path to an internal file. Pulls from temporary location if running in a bundle, otherwise resolves relative to the repository root.

    Parameters
    ----------
    parts : str
        Relative path components to the internal file. (i.e. `"dist", "file.exe"`)

    Returns
    -------
    Path
        The full path to the internal file's temporary location.
    """

    if getattr(sys, "_MEIPASS", None):
        path = Path(sys._MEIPASS)
    else:
        repo_root = Path(__file__).resolve().parents[3]
        if parts and parts[0] == "cfg":
            path = repo_root / "configs"
            parts = parts[1:]
        elif parts and parts[0] == "src":
            path = repo_root / "src" / "mo2-lint"
            parts = parts[1:]
        else:
            path = repo_root

    resolved = path.joinpath(*parts)
    logger.trace(f"Accessing internal file: {resolved}")
    return resolved
