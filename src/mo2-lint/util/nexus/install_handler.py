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

    output = Path("~/.local/share/mo2-lint/find_heroic_install").expanduser()
    output.parent.mkdir(parents=True, exist_ok=True)
    copy2(internal_file("dist", "find_heroic_install"), output)
    output.chmod(output.stat().st_mode | stat.S_IEXEC)

    output = Path(
        "~/.local/share/applications/modorganizer2-nxm-handler.desktop"
    ).expanduser()
    output.parent.mkdir(parents=True, exist_ok=True)
    copy2(internal_file("src", "modorganizer2-nxm-handler.desktop"), output)
    output.chmod(output.stat().st_mode | stat.S_IEXEC)


def set_handler():
    desktop = Path(
        "~/.local/share/applications/modorganizer2-nxm-handler.desktop"
    ).expanduser()

    import subprocess
    import shutil

    mime = shutil.which("xdg-mime")
    if mime is None:
        logger.error("xdg-mime not found; cannot register mimetype.")
        return
    subprocess.run([mime, "default", desktop.name, "x-scheme-handler/nxm"], check=True)
    logger.info("Registered nxm:// handler with xdg-mime.")


def set_variables():
    from util.variables import game_info, parameters, launcher

    dest = Path(parameters.get("directory") + "lint.env")
    if dest.exists():
        dest.open("w").close()  # Truncate
    else:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.touch()
    with dest.open("a") as f:
        f.write(f'launcher="{launcher}"\n')
        f.write(f'steam_id="{game_info.get("steam_id")}"\n')
        f.write(f'gog_id="{game_info.get("gog_id")}"\n')
        f.write(f'epic_id="{game_info.get("epic_id")}"\n')
    logger.info(f"Created variables file at {dest}")


def main():
    install_handlers()
    set_handler()
    set_variables()
    logger.success("Nexus Mods handlers installed successfully.")
