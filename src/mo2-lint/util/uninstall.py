#!/usr/bin/env python3

from util.state import state_list, state_file
from pathlib import Path
from shutil import copy2 as copy, rmtree
from send2trash import send2trash as trash


def uninstall_instance(instances: dict):
    matched = []
    matches = {}
    match_count = {}
    games = []
    for inst in instances:
        game = inst.get("nexus_id", "N/A")
        if game not in games:
            games.append(game)

    for g in games:
        match_count[g] = 0
        for inst in state_list.parsed:
            if inst.get("nexus_id", None) == g:
                matched.append(inst)
        match_count[g] += len(matched)
        matches[g] = matched.copy()
        matched.clear()

    for game, count in match_count.items():
        game_instances = [
            inst for inst in instances if inst.get("nexus_id", None) == game
        ]
        revert_gamepath = ""
        game_executable = Path(inst.get("game_install_path", None)) / inst.get(
            "game_executable", None
        )

        modified_game_install = game_executable.exists() and (
            game_executable.with_suffix(".exe.bak").exists()
            or (game_executable.parent / "modorganizer2").exists()
        )
        if count > len(game_instances) and modified_game_install:
            print(
                f"\nThere are more matching instances ({count}) than what you've marked for uninstallation ({len(instances)}) for game '{game}'."
            )
            print(
                "Reverting changes to the game executable may prevent you from launching into other instances."
            )
            revert_gamepath = input(
                "Do you want to revert the game executable changes? (y/N): "
            )
        if not modified_game_install:
            print(
                f"\nNo backup found for {game_executable.name}. You may need to manually restore the original executable ('Verify' in your game launcher). Skipping restoration."
            )
            continue

        if count == 1 or revert_gamepath.lower() == "y":
            restore_game_exec(str(game_executable))
        elif revert_gamepath.lower() == "n":
            print("Skipping restoration of game executable.")

    for inst in instances:
        delete_instance(inst)


def restore_game_exec(exec: str):
    import os

    exec = Path(exec)
    backup = exec.with_suffix(".exe.bak")
    try:
        copy(backup, exec)
        os.remove(backup)
    except FileNotFoundError:
        print(
            f"No backup found for {exec.name}. You may need to manually restore the original executable ('Verify' in your game launcher)."
        )
    try:
        rmtree(exec.parent / "modorganizer2")
    except FileNotFoundError:
        print("No redirector data folder found to remove.")


def delete_instance(inst: dict):
    path = Path(inst.get("modorganizer_path", "")).parent
    confirm = input(
        f"Are you sure you want to uninstall the instance at '{path}'? [y/t(rash)/N]: "
        # y = permanent delete, t = send to trash, N = cancel
    )
    if not confirm.lower() == "n":
        try:
            if confirm.lower() == "t":
                trash(path)
            else:
                rmtree(path)
            print(f"\nSuccessfully uninstalled instance at '{path}'.")
        except FileNotFoundError:
            print(
                f"\nInstance path '{path}' not found. It may have already been removed."
            )
        state_file.remove_instance(int(inst.get("index", -1)))
    else:
        print("Uninstallation cancelled for this instance.")


def main(game=None):
    print()

    state_list.main(game, function="uninstall")
    length = len(state_list.parsed)
    choice = []

    if length == 1:
        print("\nOnly one instance found. Proceeding to uninstall...")
        choice = state_list.parsed
    else:
        index = input("\nEnter index of instance to uninstall (or 'all'): ").strip()
        if index.isdigit():
            if not (
                index.isdigit()
                and int(index) > 0
                and int(index) < (len(state_list.parsed) + 1)
            ):
                print("Invalid index. Aborting uninstallation.")
                return
            print(f"Uninstalling instance {index}...")
            choice.append(state_list.parsed[int(index) - 1])
        elif index.lower() == "all" or index.lower() == "a":
            print("Uninstalling all matching instances...")
            choice = state_list.parsed
        else:
            print("Invalid input. Aborting uninstallation.")
            return

    uninstall_instance(choice)
