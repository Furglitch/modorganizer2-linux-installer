#!/usr/bin/env python3

from loguru import logger
from pathlib import Path
from shutil import copy2
from util.checksum import compare_checksum
from util.internal_file import internal_file as internal
import shutil
import stat
import subprocess


def install():
    """
    Install handlers for Nexus Mods (nxm://) links.
    """

    logger.info("Installing NXM:// Handlers...")

    # Install handler
    output = Path("~/.local/share/mo2-lint/nxm_handler").expanduser()
    internal_path = internal("dist", "nxm_handler")
    if not compare_checksum(internal_path, output):
        logger.info("NXM:// Handler is up to date; skipping installation.")
        return
    else:
        logger.info("Installing NXM:// Handler...")
        output.parent.mkdir(parents=True, exist_ok=True)
        copy2(internal_path, output)
        output.chmod(output.stat().st_mode | stat.S_IEXEC)

    # Install desktop entry
    output = Path(
        "~/.local/share/applications/mo2lint_nxm_handler.desktop"
    ).expanduser()
    internal_path = internal("cfg", "nxm_handler.desktop")
    if not compare_checksum(internal_path, output):
        logger.info(
            "NXM:// Handler desktop entry is up to date; skipping installation."
        )
        return
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
