#!/usr/bin/env python3

from pathlib import Path
import subprocess
import shutil
import os
from typing import List, Optional
from loguru import logger

exe = shutil.which("winetricks") or None


def run(prefix: Path, command: List[str]) -> str:
    if exe is None:
        raise FileNotFoundError(
            "winetricks executable not found in PATH. Pass its path to `apply(wine=...)` or install winetricks."
        )

    cmd = [str(exe), f"prefix={str(prefix)}"] + [str(c) for c in command]
    env = os.environ.copy()
    env.setdefault("WINEPREFIX", str(prefix))

    logger.debug(f"Running winetricks command: {' '.join(cmd)}")

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=env,
    )

    out_lines: List[str] = []
    if proc.stdout:
        for raw in proc.stdout:
            out_lines.append(raw)

    ret = proc.wait()
    if ret == 0:
        logger.info("winetricks completed successfully.")
    else:
        logger.warning(f"winetricks exited with non-zero status: {ret}")

    return "".join(out_lines)


def apply(wine: Optional[Path], prefix: Path, command: List[str]):
    logger.info(f"Applying tricks to prefix {prefix}: {command}")
    global exe
    if exe is None and wine is not None:
        exe = str(wine)

    return run(prefix, command)
