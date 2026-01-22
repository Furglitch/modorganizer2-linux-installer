#!/usr/bin/env python3

from loguru import logger
from pathlib import Path
import util.variables as var


def create_path_entry():
    game_path = Path(var.game_install_path)
    if str(game_path).endswith(".exe"):
        game_path = game_path.parent

    redir_path = Path(game_path) / "modorganizer2" / "instance_path.txt"
    mo2_path = Path(var.parameters.get("directory")) / "ModOrganizer.exe"
    logger.info(f"Creating instance path entry at {redir_path}...")

    redir_path.parent.mkdir(parents=True, exist_ok=True)
    with open(redir_path, "w", encoding="utf-8") as file:
        file.write(str(mo2_path))
    logger.debug(f"Wrote MO2 path '{mo2_path}' to '{redir_path}'.")


def install():
    from shutil import copy2
    import stat

    logger.info("Installing Redirector...")

    game_path = (
        Path(var.game_install_path)
        if not Path(var.game_install_path).is_file()
        else Path(var.game_install_path).parent
    )
    from .validation import validate_redirector as validate

    if validate(game_path):
        logger.info("Redirector is already installed and up to date.")
        return

    exec_path = game_path / var.game_info.get("executable")
    logger.debug(f"Game executable path: {exec_path}")

    exec_backup = exec_path.with_suffix(".exe.bak")
    logger.debug(f"Game executable backup path: {exec_backup}")

    if not exec_backup.exists():
        logger.info(f"Creating backup of original executable at {exec_backup}...")
        copy2(exec_path, exec_backup)

    logger.info(f"Installing Redirector executable to {exec_path}...")
    copy2(var.internal_file("dist", "redirector.exe"), exec_path)
    exec_path.chmod(exec_path.stat().st_mode | stat.S_IEXEC)


def main():
    create_path_entry()
    install()
    logger.success("Redirector installed successfully.")
