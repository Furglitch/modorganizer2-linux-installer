#!/usr/bin/env python3

from pathlib import Path
from typing import Optional
from util import lang
from util.state_file import match_instances


def list(game: Optional[str], directory: Optional[Path]):
    list = match_instances(game, directory)
    matched = ""
    if game or directory:
        matched = "matching "
    print(f"Found {len(list)} {matched}Mod Organizer 2 instance(s):")
    list = lang.list_instances(list)
    for item in list:
        print(f"  - {item}")
