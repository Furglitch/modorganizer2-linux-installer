from loguru import logger
from pathlib import Path
from typing import Optional
import json

state_file = Path("~/.config/mo2-lint/state.json").expanduser()
instances: list[dict] = []
instance: dict = {}


def load_state() -> list[dict]:
    logger.debug(f"Loading state file from: {state_file}")
    if state_file.exists():
        with state_file.open("r", encoding="utf-8") as f:
            global instances
            instances = json.load(f)
            logger.trace(f"Loaded state file: {instances}")
            instances = instances.get("instances", [])
            logger.debug(f"Loaded {len(instances)} instances from state file.")
    else:
        state_file.parent.mkdir(parents=True, exist_ok=True)
    return instances


def check_existing_instances(working_path: str) -> Optional[int]:
    logger.debug(f"Checking for existing instances for path {working_path}")
    working_path = Path(working_path).expanduser().resolve()
    global instances
    for inst in instances:
        logger.debug(f"Checking instance [{inst.get('index', '')}]")
        instance_path = Path(inst.get("instance_path", "")).expanduser().resolve()
        path_match = instance_path == working_path
        logger.debug(
            f"Instance path match: {instance_path} == {working_path} : {path_match}"
        )
        if path_match:
            return inst.get("index", 0)


def game_data(instance: int) -> dict:
    """Returns launcher, steam_ID, gog_ID, epic_ID for given instance index."""
    global instances
    for inst in instances:
        if int(inst.get("index")) == instance:
            launcher_ids = inst.get("launcher_ids", {})
            return {
                "launcher": inst.get("launcher", ""),
                "steam_id": launcher_ids.get("steam", ""),
                "gog_id": launcher_ids.get("gog", ""),
                "epic_id": launcher_ids.get("epic", ""),
            }
    return {}
