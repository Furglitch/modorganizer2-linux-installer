#!/usr/bin/env python3

from util import variables as var
from util.internal_file import internal_file
from pathlib import Path
from shutil import copyfile
from loguru import logger


def apply_workarounds():
    if var.game_info.workarounds:
        logger.info("Applying workarounds...")
        for w in var.game_info.workarounds:
            if isinstance(w, dict):
                for i in w.items():
                    t = i[0]
                    w = i[1]
                # if t == "single_executable": # Handled in util.redirector.install
                if t == "directories":
                    logger.debug("Creating workaround directories...")
                    for d in w:
                        dir_path = Path(var.game_install_path) / d
                        dir_path.mkdir(parents=True, exist_ok=True)
                if t == "files":
                    logger.debug("Creating workaround files...")
                    for f in w:
                        print(f)
                        for src, dest in f.items():
                            src = internal_file("cfg", "workarounds", src)
                            dest = Path(var.game_install_path) / dest
                            dest.parent.mkdir(parents=True, exist_ok=True)
                            copyfile(src, dest)
