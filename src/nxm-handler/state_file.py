import json
from pathlib import Path

from loguru import logger

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


def check_existing_instances(working_path: str) -> int | None:
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
    """Returns game data for a given instance index.

    Returns:
        launcher : str
            The launcher used for the instance.
        steam_id : int, optional
            The Steam App ID.
        gog_id : int, optional
            The GOG App ID.
        epic_id : str, optional
            The Epic App ID.
        launch_option_type : str, optional
            The launch option type. Used for Epic and GOG launchers to determine how to launch MO2.
        proton_version : str, optional
            The Proton version. Used for Steam launcher to determine which Proton version to use.
    """
    global instances
    for inst in instances:
        if int(inst.get("index")) == instance:
            launcher_ids = inst.get("launcher_ids", {})
            proton_wrapper = inst.get("proton_wrapper", {}) or {}
            data = {
                "launcher": inst.get("launcher", ""),
                "steam_id": launcher_ids.get("steam", ""),
                "gog_id": launcher_ids.get("gog", ""),
                "epic_id": launcher_ids.get("epic", ""),
                "launch_option_type": inst.get("launch_option_type"),
                "proton_version": proton_wrapper.get("proton_version", None),
            }
            return data
    return {}
