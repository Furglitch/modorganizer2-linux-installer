#!/usr/bin/env python3


def indent(text: str, prefix: str = "- ") -> str:
    print(f"  {prefix}{text}")


def main():
    from util.state.state_file import instances
    import util.variables as var

    print("Existing Mod Organizer 2 Instances:")
    if not instances:
        print("No instances found.")
        return

    for inst in instances:
        nexus_id = inst.get("nexus_id", "N/A")

        game_info = var.load_gameinfo(nexus_id)
        display_name = game_info.get("display", "Unknown Game")
        print(f"Instance {inst.get('index', 'N/A')} - {display_name}")
        indent(f"Path: {inst.get('modorganizer_path', 'N/A')}")
        indent(f"Launcher: {inst.get('launcher', 'N/A')}")
        for plugin in inst.get("plugins", []):
            indent(f"Plugin: {plugin}")
