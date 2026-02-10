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

    logger.debug("Installing NXM Handler.")

    # Install handler
    output = Path("~/.local/share/mo2-lint/nxm_handler").expanduser()
    internal_path = internal_file("dist", "nxm_handler")
    if output.exists() and compare_checksum(internal_path, output):
        logger.trace(
            "NXM Handler already installed and up to date. Skipping installation."
        )
    else:
        logger.trace(f"Installing NXM Handler to {output}")
        output.parent.mkdir(parents=True, exist_ok=True)
        copy2(internal_path, output)
        output.chmod(output.stat().st_mode | stat.S_IEXEC)

    # Install desktop entry
    output = Path(
        "~/.local/share/applications/mo2lint_nxm_handler.desktop"
    ).expanduser()
    internal_path = internal_file("cfg", "nxm_handler.desktop")
    if output.exists() and compare_checksum(internal_path, output):
        logger.trace(
            "NXM Handler desktop entry already installed and up to date. Skipping installation."
        )
    else:
        logger.trace(f"Installing NXM Handler desktop entry to {output}")
        output.parent.mkdir(parents=True, exist_ok=True)
        copy2(internal_path, output)
        output.chmod(output.stat().st_mode | stat.S_IEXEC)
        mime = shutil.which("xdg-mime")
        if mime is None:
            logger.warning(
                f"xdg-mime not found. Please manually set the default application for nxm:// URLs to {output}."
            )
        else:
            subprocess.run(
                [mime, "default", output.name, "x-scheme-handler/nxm"], check=True
            )

    logger.success("NXM Handler installation complete.")
