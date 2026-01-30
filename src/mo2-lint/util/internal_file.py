#!/usr/bin/env python3

from loguru import logger
from pathlib import Path
import sys


def internal_file(*parts) -> Path:
    """Get the path to an internal file within the package.

    @param path: Relative path to the internal file.
    @return: Full path to the internal file.
    """

    path = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve()))
    logger.trace(f"Resolving internal file. base={path}, parts={parts}")
    return path.joinpath(*parts)
