#!/usr/bin/env python3
"""
Generate a minimal binary appinfo.vdf (APPINFO_28 format) for the Docker
test environment.  The file contains the three entry types that protontricks
and mo2-lint/steam.py both require:

  1. Steam Play manifest  (appid 891390)   - lists the Proton compat tool
  2. Proton entry         (appid 2805730)  - name used by protontricks
  3. Game entry           (appid 22330)    - Oblivion with launch options
"""

import sys
from hashlib import sha1
from pathlib import Path
from struct import pack

# APPINFO_28 constants
MAGIC = 0x107564428  # 8-byte LE uint64
TYPE_DICT = b"\x00"
TYPE_STRING = b"\x01"
TYPE_INT32 = b"\x02"
SECTION_END = b"\x08"

# App IDs
STEAM_PLAY_APPID = 891390
PROTON_APPID = 2805730  # Proton 10.0
PROTON_KEY = "proton_10"
PROTON_ALIASES = "proton-10,proton_10"
PROTON_NAME = "Proton 10.0"
GAME_APPID = 22330  # Oblivion GOTY


def _str(s: str) -> bytes:
    return s.encode("utf-8") + b"\x00"


def _u32(i: int) -> bytes:
    return pack("<I", i)


def _encode(data: dict) -> bytes:
    """Recursively encode a dict as binary VDF subsections."""
    out = bytearray()
    for key, value in data.items():
        key_bytes = _str(key)
        if isinstance(value, dict):
            out += TYPE_DICT + key_bytes + _encode(value)
        elif isinstance(value, str):
            out += TYPE_STRING + key_bytes + _str(value)
        elif isinstance(value, int):
            out += TYPE_INT32 + key_bytes + _u32(value)
        else:
            raise TypeError(
                f"Unsupported VDF value type for key '{key}': {type(value)}"
            )
    out += SECTION_END
    return bytes(out)


def _entry(appid: int, sections: dict) -> bytes:
    """Build a full binary app entry (header + sections)."""
    sections_bytes = _encode(sections)

    checksum_text = bytes(20)
    checksum_binary = sha1(sections_bytes).digest()
    state = 4
    last_update = 0
    access_token = 0
    change_number = 0

    tail = (
        _u32(state)
        + _u32(last_update)
        + pack("<Q", access_token)
        + checksum_text
        + _u32(change_number)
        + checksum_binary
        + sections_bytes
    )

    return _u32(appid) + _u32(len(tail)) + tail


#  Entry builders


def _steam_play_entry() -> bytes:
    """
    Steam Play manifest - protontricks checks for appid 891390 and reads
    extended.compat_tools to discover Proton installations.
    """
    return _entry(
        STEAM_PLAY_APPID,
        {
            "appinfo": {
                "appid": STEAM_PLAY_APPID,
                "extended": {
                    "app_mappings": {},
                    "compat_tools": {
                        PROTON_KEY: {
                            "appid": PROTON_APPID,
                            "aliases": PROTON_ALIASES,
                        }
                    },
                },
            }
        },
    )


def _proton_entry() -> bytes:
    """Proton installation entry - protontricks reads common.name."""
    return _entry(
        PROTON_APPID,
        {
            "appinfo": {
                "appid": PROTON_APPID,
                "common": {"name": PROTON_NAME},
                "config": {"installdir": PROTON_NAME},
            }
        },
    )


def _game_entry() -> bytes:
    """
    Oblivion entry - mo2-lint/steam.py reads config.installdir and
    config.launch to display and add launch options.
    """
    return _entry(
        GAME_APPID,
        {
            "appinfo": {
                "appid": GAME_APPID,
                "config": {
                    "installdir": "Oblivion",
                    "launch": {
                        "0": {
                            "executable": "OblivionLauncher.exe",
                            "type": "default",
                            "oslist": "windows",
                        }
                    },
                },
            }
        },
    )


# Main
def build() -> bytes:
    out = bytearray()
    out += pack("<Q", MAGIC)
    out += _steam_play_entry()
    out += _proton_entry()
    out += _game_entry()
    out += b"\x00\x00\x00\x00"
    return bytes(out)


if __name__ == "__main__":
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("appinfo.vdf")
    output.parent.mkdir(parents=True, exist_ok=True)
    data = build()
    output.write_bytes(data)
    print(f"Generated binary appinfo.vdf → {output} ({len(data)} bytes)")
