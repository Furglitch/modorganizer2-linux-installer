#!/usr/bin/env python3
"""Facts about the machine MO2-LINT runs on."""

import platform
from pathlib import Path


def machine() -> str:
    """Return a canonical architecture name for the host."""
    name = platform.machine().lower()
    return {"amd64": "x86_64", "arm64": "aarch64"}.get(name, name)


def is_x86_64() -> bool:
    return machine() == "x86_64"


def is_arm64() -> bool:
    return machine() == "aarch64"


def is_steam_frame() -> bool:
    """Identify SteamOS VR, where restarting Steam ends the whole VR session."""
    try:
        text = Path("/etc/os-release").read_text(encoding="utf-8")
    except OSError:
        return False
    values = {}
    for line in text.splitlines():
        key, separator, value = line.partition("=")
        if separator:
            values[key.strip()] = value.strip().strip("\"'")
    return values.get("ID") == "steamos" and values.get("VARIANT_ID") == "vr"
