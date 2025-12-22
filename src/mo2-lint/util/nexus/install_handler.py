#!/usr/bin/env python3

from loguru import logger
from pathlib import Path


def install_handlers():
    from shutil import copy2
    from util.variables import internal_file
    import stat

    logger.info("Installing Nexus Mods handlers...")

    output = Path("~/.local/share/mo2-lint/nxm_handler").expanduser()
    output.parent.mkdir(parents=True, exist_ok=True)
    copy2(internal_file("dist", "nxm_handler"), output)
    output.chmod(output.stat().st_mode | stat.S_IEXEC)

    output = Path(
        "~/.local/share/applications/mo2lint_nxm_handler.desktop"
    ).expanduser()
    output.parent.mkdir(parents=True, exist_ok=True)
    copy2(internal_file("cfg", "nxm_handler.desktop"), output)
    output.chmod(output.stat().st_mode | stat.S_IEXEC)


def set_handler():
    desktop = Path(
        "~/.local/share/applications/mo2lint_nxm_handler.desktop"
    ).expanduser()

    import subprocess
    import shutil

    mime = shutil.which("xdg-mime")
    if mime is None:
        logger.error("xdg-mime not found; cannot register mimetype.")
        return
    subprocess.run([mime, "default", desktop.name, "x-scheme-handler/nxm"], check=True)
    logger.info("Registered nxm:// handler with xdg-mime.")


def main():
    install_handlers()
    set_handler()
    logger.success("Nexus Mods handlers installed successfully.")
