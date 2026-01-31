#!/usr/bin/env python3

from loguru import logger
from pathlib import Path
from shutil import copy2
from util.checksum import compare_checksum
from util.internal_file import internal_file
import shutil
import stat
import subprocess


def install():
    """
    Install nxm_handler and its desktop entry.
    """

    logger.info("Installing NXM:// Handlers...")

    # Install handler
    output = Path("~/.local/share/mo2-lint/nxm_handler").expanduser()
    internal_path = internal_file("dist", "nxm_handler")
    if output.exists() and compare_checksum(internal_path, output):
        logger.info("NXM:// Handler is up to date; skipping installation.")
    else:
        logger.info("Installing NXM:// Handler...")
        output.parent.mkdir(parents=True, exist_ok=True)
        copy2(internal_path, output)
        output.chmod(output.stat().st_mode | stat.S_IEXEC)

    # Install desktop entry
    output = Path(
        "~/.local/share/applications/mo2lint_nxm_handler.desktop"
    ).expanduser()
    internal_path = internal_file("cfg", "nxm_handler.desktop")
    if output.exists() and compare_checksum(internal_path, output):
        logger.info(
            "NXM:// Handler desktop entry is up to date; skipping installation."
        )
    else:
        logger.info("Installing NXM:// Handler desktop entry...")
        output.parent.mkdir(parents=True, exist_ok=True)
        copy2(internal_path, output)
        output.chmod(output.stat().st_mode | stat.S_IEXEC)
        mime = shutil.which("xdg-mime")
        if mime is None:
            logger.error("xdg-mime not found; cannot register mimetype.")
        else:
            subprocess.run(
                [mime, "default", output.name, "x-scheme-handler/nxm"], check=True
            )

    logger.success("NXM:// Handlers installed successfully.")
