#!/usr/bin/env python3

from pathlib import Path
from typing import Optional
from util.state_file import match_instances


def list(game: Optional[str], directory: Optional[Path]):
    list = match_instances(game, directory)
    matched = ""
    if game or directory:
        matched = "matching "
    print(f"Found {len(list)} {matched}Mod Organizer 2 instance(s):")
    for idx, inst in enumerate(list, start=1):
        print(
            f"    - [{idx}] Game: {inst.nexus_slug}, Path: {inst.instance_path}, Script Extender: {'Yes' if inst.script_extender else 'No'}, Plugins: {', '.join(inst.plugins) if inst.plugins else 'None'}"
        )
