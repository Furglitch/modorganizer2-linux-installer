#!/usr/bin/env python3


def indent(text: str, prefix: str = "- ") -> str:
    print(f"  {prefix}{text}")


parsed = []


def main(game=None, directory=None, function=None):
    from util.state.state_file import instances
    import util.variables as var

    prefix = "Matching" if game else "Existing"
    print(f"{prefix} Mod Organizer 2 Instances:")
    if not instances:
        print("No instances found.")
        return

    for i, inst in enumerate(instances, start=1):
        nexus_id = inst.get("nexus_id", "N/A")
        path = inst.get("modorganizer_path", "N/A")
        if game:
            if nexus_id != game:
                continue
        if directory:
            directory = directory.removesuffix("/")
            if path.endswith("ModOrganizer.exe"):
                path = path.removesuffix("ModOrganizer.exe")
            if not path.startswith(directory):
                continue

        game_info = var.load_gameinfo(nexus_id)
        display_name = (
            game_info.get("display", "Unknown Game")
            if not (function and not game_info)
            else inst.get("nexus_id", "N/A")
        )
        print(f"Instance {i} - {display_name}")
        indent(f"Path: {path}")
        indent(f"Launcher: {inst.get('launcher', 'N/A')}")
        for plugin in inst.get("plugins", []):
            indent(f"Plugin: {plugin}")
        parsed.append(inst)
