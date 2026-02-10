#!/usr/bin/env python3

from loguru import logger
from pathlib import Path
from shutil import copyfile
from util import variables as var, state_file as state
from util.internal_file import internal_file


def apply_workarounds():
    if var.game_info.workarounds:
        logger.info(f"Applying workarounds for {var.game_info.display_name}")
        for w in var.game_info.workarounds:
            if isinstance(w, dict):
                for i in w.items():
                    t = i[0]
                    w = i[1]
                # if t == "single_executable": # Handled in util.redirector.install
                if t == "directories":
                    logger.debug(f"Creating directories for workaround: {w}")
                    for d in w:
                        dir_path = Path(state.current_instance.game_path) / d
                        dir_path.mkdir(parents=True, exist_ok=True)
                        logger.trace(f"Created directory: {dir_path}")
                if t == "files":
                    logger.debug(f"Copying files for workaround: {w}")
                    for f in w:
                        for src, dest in f.items():
                            src = internal_file("cfg", "workarounds", src)
                            dest = Path(state.current_instance.game_path) / dest
                            dest.parent.mkdir(parents=True, exist_ok=True)
                            copyfile(src, dest)
                            logger.trace(f"Copied file from {src} to {dest}")
                if t == "needs_java" and w is True:
                    from .external_resources import download_java

                    logger.debug("Downloading Java for workaround: needs_java")
                    download_java()
