#!/usr/bin/env python3
"""Facts about the machine MO2-LINT runs on."""

import platform


def machine() -> str:
    """Return a canonical architecture name for the host."""
    name = platform.machine().lower()
    return {"amd64": "x86_64", "arm64": "aarch64"}.get(name, name)


def is_x86_64() -> bool:
    return machine() == "x86_64"
