#!/usr/bin/env python3

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from loguru import logger
from uuid import UUID
import json
from util.variables import LauncherIDs


@dataclass
class NexusAPIData:
    """
    Stores Nexus Mods API credentials.

    Parameters
    ----------
    uuid : UUID
        The UUID associated with the Nexus Mods API.
    connection_token : str
        The connection token for the Nexus Mods API.
    api_key : str
        The API key for the Nexus Mods API.
    """

    uuid: UUID = None
    connection_token: str = None
    api_key: str = None

    @classmethod
    def from_dict(cls, data: Optional[dict[str, any]]):
        if not data:
            return None
        return cls(
            uuid=UUID(data["uuid"]),
            connection_token=data["connection_token"],
            api_key=data["api_key"],
        )

    @classmethod
    def to_dict(cls, data: "NexusAPIData") -> dict[str, any]:
        return {
            "uuid": str(data.uuid),
            "connection_token": data.connection_token,
            "api_key": data.api_key,
        }

    def __post_init__(self):
        if not self.uuid:
            logger.warning("Nexus API UUID must be provided.")
        if not self.connection_token:
            logger.warning("Nexus API connection token must be provided.")
        if not self.api_key:
            logger.warning("Nexus API key must be provided.")


@dataclass
class InstanceData:
    """
    Stores data about an installed Mod Organizer 2 instance.

    Parameters
    ----------
    nexus_slug : str
        The Nexus Mods slug identifier for the game associated with this MO2 instance.
    instance_path : Path
        Directory path where this MO2 instance is installed.
    launcher : str
        Name of the game launcher for this instance.
    launcher_ids : LauncherIDs
        Launcher-specific IDs for the game.
    game_path : Path
        Installation path of the game associated with this MO2 instance.
    game_executable : str
        Executable filename for the game.
    plugins : list[str], optional
        List of plugins enabled for this MO2 instance.
    """

    from util.variables import LauncherIDs

    index: int = None
    nexus_slug: str = None
    instance_path: Path = None
    launcher: str = None
    launcher_ids: LauncherIDs = None
    game_path: Path = None
    game_executable: str = None
    script_extender: bool = False
    plugins: Optional[list[str]] = None

    @classmethod
    def from_dict(cls, data: Optional[dict[str, any]]):
        if not data:
            return None
        return cls(
            index=data.get("index", None),
            nexus_slug=data.get("nexus_slug"),
            instance_path=Path(data.get("instance_path")),
            launcher=data.get("launcher"),
            launcher_ids=LauncherIDs.from_dict(data.get("launcher_ids")),
            game_path=Path(data.get("game_path")),
            game_executable=data.get("game_executable"),
            plugins=data.get("plugins", []),
        )

    @classmethod
    def to_dict(cls, data: "InstanceData") -> dict[str, any]:
        return {
            "index": data.index,
            "nexus_slug": data.nexus_slug,
            "instance_path": str(data.instance_path),
            "launcher": data.launcher,
            "launcher_ids": LauncherIDs.to_dict(data.launcher_ids),
            "game_path": str(data.game_path),
            "game_executable": data.game_executable,
            "plugins": data.plugins,
        }

    def __post_init__(self):
        from util.variables import plugin_info

        if not self.nexus_slug:
            logger.warning("InstanceData requires a valid nexus_slug.")
        if not self.instance_path:
            logger.warning("InstanceData requires a valid instance_path.")
        if not self.launcher:
            logger.warning("Launcher name should be provided for InstanceData.")
        if not self.launcher_ids:
            logger.warning("Launcher IDs should be provided for InstanceData.")
        if not self.game_path:
            logger.warning(
                "Game installation path should be provided for InstanceData."
            )
        if not self.game_executable:
            logger.warning("Game executable should be provided for InstanceData.")
        if self.plugins is None:
            self.plugins = []
        elif any(plugin not in plugin_info for plugin in self.plugins):
            logger.warning("One or more plugins are not recognized in plugin_info.")


@dataclass
class StateFile:
    """
    Represents the state file JSON storing MO2 instances and Nexus API data.
    """

    nexus_api: Optional[NexusAPIData] = None
    instances: list[InstanceData] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Optional[dict[str, any]]):
        if not data:
            return None
        return cls(
            nexus_api=NexusAPIData.from_dict(data.get("nexus_api")),
            instances=[
                InstanceData.from_dict(inst_data)
                for inst_data in data.get("instances", [])
            ],
        )

    @classmethod
    def to_dict(cls, state_file: "StateFile") -> dict[str, any]:
        return {
            "nexus_api": NexusAPIData.to_dict(state_file.nexus_api),
            "instances": [InstanceData.to_dict(inst) for inst in state_file.instances],
        }


state_file: StateFile = None
filepath = Path("~/.config/mo2-lint/instance_state.json").expanduser()


def load_state_file():
    """
    Loads the state file from disk into the global state_file variable.
    If the file does not exist, initializes an empty StateFile.
    """
    global state_file
    if filepath.exists():
        with filepath.open("r", encoding="utf-8") as f:
            data = json.load(f)
            logger.trace(f"Loaded state file: {data}")
            state_file = StateFile.from_dict(data)
    else:
        state_file = StateFile(None, [])


existing_indexes: list[InstanceData] = []


def check_instance(
    game: Optional[str], directory: Optional[Path]
) -> list[InstanceData]:
    """
    Checks for existing MO2 instances in state_file that match the given game or directory.

    Parameters
    ----------
    game : str, optional
        Nexus Mods slug identifier for the game.
    directory : Path, optional
        Directory path to check for existing MO2 instances. Checks subdirectories as well.

    Returns
    -------
    list[InstanceData]
        List of InstanceData objects that match the given game and/or directory.

    Raises
    -------
    ValueError
        If both game and directory are not provided.
    """
    if game is None and directory is None:
        raise ValueError("Either game or directory must be provided to check_instance.")
    logger.debug(
        f"Checking for instances with nexus slug: {game} or directory: {directory}"
    )
    global state_file, existing_indexes
    existing_indexes = []
    for instance in state_file.instances:
        if instance.instance_path == directory or instance.nexus_slug == game:
            logger.info(
                f"Found matching instance at index {instance.index}: {instance}"
            )
            existing_indexes.append(instance)
    return existing_indexes


available_indexes: list[InstanceData] = []
current_instance: InstanceData = InstanceData(
    index=None,
    nexus_slug=None,
    instance_path=None,
    launcher=None,
    launcher_ids=None,
    game_path=None,
    game_executable=None,
    plugins=[],
)


def choose_instance():
    """
    Prompts the user to choose between using an existing instance or creating a new one.
    """
    global current_instance
    if existing_indexes:
        quantifier = "the" if len(existing_indexes) == 1 else "an"
        choice = (
            input(
                f"Would you like to use {quantifier} existing instance [e] or create a new one? [n]: "
            )
            .strip()
            .lower()
        )
        if choice == "e":
            global available_indexes
            available_indexes = []
            if len(existing_indexes) == 1:
                current_instance = existing_indexes[0]
            elif len(existing_indexes) > 1:
                for i, inst in enumerate(existing_indexes):
                    available_indexes.append(inst.index)
                selected = int(
                    input("Select the number of the instance you want to use: ")
                )
                selected_index = available_indexes[selected - 1]
                current_instance = selected_index
        elif choice != "n":
            raise ValueError("Invalid choice made when selecting instance.")
        return
    set_index(None)


def set_index(index: Optional[int] = None):
    """
    Sets the current instance index in the state_file.

    Parameters
    ----------
    index : int, optional
        Specific index to set for the current instance. If None, assigns the next available index.
    """
    global state_file
    max = 0
    if not index:
        for inst in state_file.instances:
            if inst.index and inst.index > max:
                max = inst.index
        set = max + 1
    else:
        if index not in [inst.index for inst in state_file.instances]:
            set = index
    current_instance.index = set


def remove_instance(index: int):
    global state_file
    state_file.instances = [
        inst for inst in state_file.instances if inst.index != index
    ]
    logger.debug(
        f"Removed instance with index {index}. Remaining instances: {len(state_file.instances)}"
    )
    write_state(add_current=False)


def write_state(add_current: bool = True):
    global state_file, current_instance
    if {} in state_file.instances:
        state_file.instances.remove({})
    if add_current and current_instance not in state_file.instances:
        state_file.instances.append(current_instance)

    with filepath.open("w", encoding="utf-8") as f:
        json.dump(StateFile.to_dict(state_file), f, indent=2)
    logger.debug(f"Wrote state file with {len(state_file.instances)} instances.")
