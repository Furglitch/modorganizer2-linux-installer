#!/usr/bin/env python3

from loguru import logger
from pathlib import Path
from shutil import copy2
import stat
import shutil
import subprocess
from util.internal_file import internal_file as internal
from util.checksum import compare_checksum


def install():
    """
    Install handlers for Nexus Mods (nxm://) links.
    """

    logger.info("Installing Nexus Mods handlers...")

    # Install handler
    output = Path("~/.local/share/mo2-lint/nxm_handler").expanduser()
    internal_path = internal("dist", "nxm_handler")
    if not compare_checksum(internal_path, output):
        logger.info("Nexus Mods handler is up to date; skipping installation.")
        return
    else:
        output.parent.mkdir(parents=True, exist_ok=True)
        copy2(internal_path, output)
        output.chmod(output.stat().st_mode | stat.S_IEXEC)

    # Install desktop entry
    output = Path(
        "~/.local/share/applications/mo2lint_nxm_handler.desktop"
    ).expanduser()
    internal_path = internal("cfg", "nxm_handler.desktop")
    if not compare_checksum(internal_path, output):
        logger.info("Nexus Mods desktop entry is up to date; skipping installation.")
        return
    else:
        output.parent.mkdir(parents=True, exist_ok=True)
        copy2(internal_path, output)
        output.chmod(output.stat().st_mode | stat.S_IEXEC)
        mime = shutil.which("xdg-mime")
        if mime is None:
            logger.error("xdg-mime not found; cannot register mimetype.")
            return
        subprocess.run(
            [mime, "default", output.name, "x-scheme-handler/nxm"], check=True
        )

    logger.success("Nexus Mods handlers installed successfully.")
