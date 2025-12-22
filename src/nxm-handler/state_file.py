from loguru import logger
from pathlib import Path
import json

state_file = Path("~/.config/mo2-lint/instance_state.json").expanduser()
instances = []
instance = {}


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


def check_existing_instances(working_path: str):
    logger.debug(f"Checking for existing instances for path {working_path}")
    working_path = Path(working_path).expanduser().resolve()
    if not working_path.name.lower().endswith("modorganizer2.exe"):
        working_path = working_path / "ModOrganizer2.exe"
    global instances
    for inst in instances:
        logger.debug(f"Checking instance [{inst.get('index', '')}]")
        instance_path = Path(inst.get("modorganizer_path", "")).expanduser().resolve()
        path_match = instance_path == working_path
        logger.debug(f"Instance path match: {instance_path} {path_match}")
        if path_match:
            return inst.get("index", 0)


def game_data(instance: int) -> dict:
    """Returns launcher, steam_ID, gog_ID, epic_ID for given instance index."""
    global instances
    for inst in instances:
        if int(inst.get("index")) == instance - 1:
            launcher_ids = inst.get("launcher_ids", {})
            return {
                "launcher": inst.get("launcher", ""),
                "steam_id": launcher_ids.get("steam", ""),
                "gog_id": launcher_ids.get("gog", ""),
                "epic_id": launcher_ids.get("epic", ""),
            }
    return {}
