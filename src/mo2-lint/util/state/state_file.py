#!/usr/bin/env python3

from loguru import logger
from pathlib import Path
import uuid
import json

state_file = Path("~/.config/mo2-lint/instance_state.json").expanduser()
nexus_api = {}
instances = []
instance = {}
existing_index = []


def load_state() -> list[dict]:
    logger.debug(f"Loading state file from: {state_file}")
    global instances, nexus_api
    if state_file.exists():
        with state_file.open("r", encoding="utf-8") as f:
            data = json.load(f)
            logger.trace(f"Loaded state file: {data}")
            nexus_api = data.get("nexus_api", {})
            logger.debug(f"Nexus API data: {nexus_api}")
            instances = data.get("instances", [])
            logger.debug(f"Loaded {len(instances)} instances from state file.")
    else:
        state_file.parent.mkdir(parents=True, exist_ok=True)
        write_state()
    return instances


def check_existing_instances(working_path: str, working_game: str):
    logger.debug(
        f"Checking for existing instances for game {working_game} or path {working_path}"
    )
    working_path = Path(working_path).expanduser().resolve()
    global instances, existing_index
    for inst in instances:
        logger.trace(f"Checking instance [{inst.get('index', '')}]")
        instance_path = Path(inst.get("modorganizer_path", "")).expanduser().resolve()
        nexus_id = inst.get("nexus_id", "")
        path_match = instance_path == working_path
        game_match = nexus_id == working_game
        logger.trace(
            f"Instance path match: {instance_path} {path_match}, Game match: {nexus_id} {game_match}"
        )
        if (path_match or game_match) and inst not in existing_index:
            logger.info(
                f"Found existing instance: Index: {inst.get('index', '')}, Path: {inst.get('modorganizer_path', '')}, Nexus ID: {inst.get('nexus_id', '')}"
            )
            if path_match:
                existing_index.clear()
            existing_index.append(inst)
            if path_match:
                break


def select_index():
    if existing_index:
        choice = prompt_index()
        logger.debug(f"User selected index: {choice}")
        if choice == 0:
            set_index(next_index())
        else:
            global instance, instances
            instance = instances[choice - 1]
            set_index(int(instance.get("index", 0)))
    else:
        logger.debug(f"No existing instance found, assigning new index: {next}")
        set_index(next_index())
    logger.debug(f"Current instance data: {instance}")


def prompt_index() -> int:
    if existing_index:
        print("Would you like to use an existing instance or create a new one?")
        choice = (
            input("Type 'e' to use an existing instance, or 'n' to create a new one: ")
            .strip()
            .lower()
        )
        if choice == "e":
            if len(existing_index) == 1:
                return 1
            elif len(existing_index) > 1:
                print("Multiple existing instances found:")
                for i, inst in enumerate(existing_index):
                    print(f"{i + 1}: {inst.get('modorganizer_path', '')}")
                selected = int(
                    input("Select the number of the instance you want to use: ")
                )
                selected_index = int(existing_index[selected - 1].get("index", 0))
                return selected_index
        elif choice == "n":
            return 0
    else:
        return 0


def next_index() -> int:
    global instances
    max_index = 0
    for inst in instances:
        idx = int(inst.get("index", 0))
        if idx > max_index:
            max_index = idx
    new_index = max_index + 1
    return new_index


def set_index(index: int):
    global instance
    logger.debug(f"Setting instance index to: {index}")
    instance["index"] = index


def set_nexus_id(nexus_id: str):
    global instance
    logger.debug(f"Setting instance nexus_id to: {nexus_id}")
    instance["nexus_id"] = nexus_id


def set_instance_path(path: Path):
    global instance
    path = Path(path).expanduser().resolve()
    if path.exists() and path.is_dir():
        path = path / "ModOrganizer2.exe"
    elif not path.exists() and not path.name.lower().endswith("ModOrganizer2.exe"):
        path.mkdir(parents=True, exist_ok=True)
        path = path / "ModOrganizer2.exe"
    logger.debug(f"Setting instance path to: {path}")
    instance["modorganizer_path"] = str(path)


def set_launcher(launcher: str):
    global instance
    logger.debug(f"Setting instance launcher to: {launcher}")
    instance["launcher"] = launcher


def set_launcher_ids(steam_id: int = None, gog_id: int = None, epic_id: str = None):
    global instance
    logger.debug(
        f"Setting instance launcher IDs to: steam={steam_id}, gog={gog_id}, epic={epic_id}"
    )
    launcher_ids = {"steam": steam_id, "gog": gog_id, "epic": epic_id}
    instance["launcher_ids"] = launcher_ids


def set_plugins(plugins: list[str]):
    global instance
    logger.debug(f"Setting instance plugins to: {plugins}")
    instance["plugins"] = plugins


def set_nexus_uuid(id: uuid.UUID | str):
    global nexus_api
    if isinstance(id, uuid.UUID):
        nexus_api["uuid"] = str(id)
    else:
        nexus_api["uuid"] = id


def set_nexus_connection_token(token: str):
    global nexus_api
    nexus_api["connection_token"] = token


def set_nexus_api_key(token: str):
    global nexus_api
    nexus_api["api_key"] = token


def write_state():
    """Writes current state to disk."""
    with state_file.open("w", encoding="utf-8") as f:
        global instances
        if {} in instances:
            instances.remove({})
        if instance not in instances:
            instances.append(instance)
        json.dump({"nexus_api": nexus_api, "instances": instances}, f, indent=2)
        logger.debug(f"Wrote state file with {len(instances)} instances.")
