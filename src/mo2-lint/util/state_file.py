#!/usr/bin/env python3

from dataclasses import dataclass, field
from loguru import logger
from pathlib import Path
from pydantic_core import to_json
from send2trash import send2trash
from shutil import move, rmtree
from typing import Optional
from util import lang, variables as var, state_file as state
from uuid import UUID
import json


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
    def from_dict(
        cls, data: dict[str, any] | "NexusAPIData"
    ) -> Optional["NexusAPIData"]:
        if isinstance(data, cls):
            return data
        return cls(
            uuid=UUID(data.get("uuid")),
            connection_token=data.get("connection_token"),
            api_key=data.get("api_key"),
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
    game : str
        The cli parameter used to identify the game associated with this MO2 instance.
    nexus_slug : str
        The Nexus Mods slug identifier for the game associated with this MO2 instance.
    instance_path : Path
        Directory path where this MO2 instance is installed.
    pin : bool
        Whether this instance is pinned to a specific MO2 version.
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

    Raises
    ------
    TypeError
        If launcher_ids is not of type LauncherIDs.
    """

    index: int = None
    game: str = None
    nexus_slug: str = None
    instance_path: Path = None
    pin: bool = False
    launcher: str = None
    launcher_ids: var.LauncherIDs = None
    game_path: Path = None
    game_executable: str = None
    script_extender: bool = False
    plugins: Optional[list[str]] = None

    @classmethod
    def from_dict(cls, data: dict[str, any] | "InstanceData") -> "InstanceData":
        if isinstance(data, cls):
            return data
        return cls(
            index=data.get("index"),
            game=data.get("game"),
            nexus_slug=data.get("nexus_slug"),
            instance_path=Path(data.get("instance_path")),
            pin=data.get("pin", False),
            launcher=data.get("launcher"),
            launcher_ids=var.LauncherIDs.from_dict(data.get("launcher_ids")),
            game_path=Path(data.get("game_path")),
            game_executable=data.get("game_executable"),
            plugins=data.get("plugins"),
        )

    @classmethod
    def to_dict(cls, data: "InstanceData") -> dict[str, any]:
        if isinstance(data.launcher_ids, dict):
            logger.error("launcher_ids must be of type LauncherIDs, not dict.")
            raise TypeError("launcher_ids must be of type LauncherIDs, not dict.")
        return {
            "index": data.index,
            "game": data.game,
            "nexus_slug": data.nexus_slug,
            "instance_path": str(data.instance_path),
            "pin": data.pin,
            "launcher": data.launcher,
            "launcher_ids": var.LauncherIDs.to_dict(data.launcher_ids),
            "game_path": str(data.game_path),
            "game_executable": data.game_executable,
            "plugins": data.plugins,
        }

    def __post_init__(self):
        if not self.game or self.game not in var.games_info.keys():
            logger.warning("InstanceData requires a valid game identifier.")
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
        elif any(plugin not in var.plugin_info for plugin in self.plugins):
            logger.warning("One or more plugins are not recognized in plugin_info.")


@dataclass
class StateFile:
    """
    Represents the state file JSON storing MO2 instances and Nexus API data.
    """

    nexus_api: Optional[NexusAPIData] = None
    instances: list[InstanceData] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, any] | "StateFile") -> "StateFile":
        if isinstance(data, cls):
            return data
        return cls(
            nexus_api=NexusAPIData.from_dict(data.get("nexus_api"))
            if data.get("nexus_api")
            else None,
            instances=[
                InstanceData.from_dict(inst_data)
                for inst_data in data.get("instances", [])
            ],
        )

    @classmethod
    def to_dict(cls, state: "StateFile") -> dict[str, any]:
        return {
            "nexus_api": NexusAPIData.to_dict(state.nexus_api)
            if state.nexus_api
            else None,
            "instances": [InstanceData.to_dict(inst) for inst in state.instances],
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
        try:
            with filepath.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            logger.exception(
                f"Failed to parse state file JSON: {e}", backtrace=True, diagnose=True
            )
            logger.error("State file may be corrupted. Please validate or delete it.")
            logger.critical("Aborting...")
            raise SystemExit(1)
        logger.trace(f"Loaded state file: {data}")
        state_file = StateFile.from_dict(data)
    else:
        state_file = StateFile(None, [])


current_instance: InstanceData = None


def set_index(index: Optional[int] = None):
    """
    Sets the current instance index in the state_file.

    Parameters
    ----------
    index : int, optional
        Specific index to set for the current instance. If None, assigns the next available index.
    """
    global state_file, current_instance
    max = 0
    if not index:
        for inst in state_file.instances:
            if inst.index and inst.index > max:
                max = inst.index
        set = max + 1
        logger.debug(f"Assigned new index {set} to current instance.")
    else:
        if index not in [inst.index for inst in state_file.instances]:
            set = index
            logger.debug(f"Set current instance index to {set}.")
        else:
            logger.error(f"Index {index} is already in use.")
            raise ValueError(f"Index {index} is already in use.")
    current_instance.index = set


def remove_instance(instance: InstanceData, types: list[str] = ["symlink", "state"]):
    """
    Removes an instance by its index.

    Parameters
    ----------
    instance : InstanceData
        The instance to be removed.
    types : list[str], optional
        Types of removal to perform. Options are "symlink", "install", and "state".\n
        "symlink" removes the symlink to the instance.\n
        "install" removes the installation of the instance.\n
        "state" removes the state file entry for the instance.\n
    """

    if "symlink" in types:
        symlink_path = Path("~/.config/mo2-lint/instances").expanduser() / str(
            instance.index
        )
        if symlink_path.exists() or symlink_path.is_symlink():
            symlink_path.unlink()
            logger.debug(
                f"Removed symlink at {symlink_path} for instance {instance.index}"
            )
        else:
            if symlink_path.exists():
                logger.warning(
                    f"Path {symlink_path} exists but is not a symlink. Skipping removal."
                )
            else:
                logger.debug(
                    f"No symlink found at {symlink_path} for instance {instance.index}. Skipping removal."
                )

    if "install" in types:
        instance_path = instance.instance_path
        if instance_path.exists():
            if not lang.prompt_uninstall_trash():
                logger.info(f"Sending instance at {instance_path} to trash.")
                send2trash(instance_path)
            else:
                if lang.prompt_uninstall_trash_confirm():
                    logger.info(f"Permanently deleting instance at {instance_path}.")
                    rmtree(instance_path)
                else:
                    logger.info(f"Instance at {instance_path} sent to trash instead.")
                    send2trash(instance_path)

        # Restore game executable if it was backed up
        exec = (
            instance.game_executable.get(instance.launcher)
            if isinstance(instance.game_executable, dict)
            else instance.game_executable
        )
        game_exec = instance.game_path / exec
        if game_exec.exists():
            data_dir = game_exec.parent / "modorganizer2"
            if data_dir.exists() and data_dir.is_dir():
                rmtree(data_dir)

            if not var.game_info:
                var.load_game_info(instance.nexus_slug)

            backup_exec = (
                Path(str(game_exec.with_suffix("")) + ".bak.exe")
                if var.game_info.workarounds
                and any(
                    isinstance(w, dict) and w.get("single_executable") is True
                    for w in var.game_info.workarounds
                )
                else Path(str(game_exec) + ".bak")
            )
            if backup_exec.exists():
                move(backup_exec, game_exec)
                logger.debug(
                    f"Restored original game executable from backup for {game_exec}."
                )
            else:
                logger.warning(f"No backup found for {game_exec}.")
                logger.warning(
                    "It may already have been restored, or you may need to manually restore the original executable ('Verify' in your game launcher)."
                )

        logger.debug(
            f"Removed installation at {instance_path} for instance {instance.index}"
        )

    if "state" in types:
        global state_file
        state_file.instances = [
            inst for inst in state_file.instances if inst.index != instance.index
        ]
        logger.debug(f"Removed instance {instance.index} from state file.")

    write_state(False)


def write_state(add_current: bool = True):
    global state_file, current_instance
    if {} in state_file.instances:
        logger.info("Removing empty instance entries from state file.")
        state_file.instances.remove({})
    if add_current and current_instance.index not in [
        inst.index for inst in state_file.instances
    ]:
        logger.info(f"Adding current instance {current_instance.index} to state file.")
        state_file.instances.append(state.InstanceData.from_dict(current_instance))
    elif add_current and current_instance.index in [
        inst.index for inst in state_file.instances
    ]:
        logger.info(
            f"Updating current instance {current_instance.index} in state file."
        )
        for i, inst in enumerate(state_file.instances):
            if inst.index == current_instance.index:
                state_file.instances[i] = state.InstanceData.from_dict(current_instance)

    json = to_json(StateFile.to_dict(state_file), indent=2).decode("utf-8")
    with filepath.open("w", encoding="utf-8") as f:
        f.write(json)
    logger.debug(f"Wrote state file with {len(state_file.instances)} instances.")


def match_instances(
    game: Optional[str] = None, directory: Optional[Path] = None, exact: bool = False
) -> dict[InstanceData]:
    """
    Matches instances in the state_file based on the provided game or directory.

    Parameters
    ----------
    game : str, optional
        Nexus Mods slug identifier for the game to match.
    directory : Path, optional
        Directory path to match instances against.

    Returns
    -------
    dict
        A dictionary of matched instances.
    """

    global state_file
    matched: list[InstanceData] = []

    if not state_file.instances:
        logger.warning("No instances found that match the criteria.")
        return

    for instance in state_file.instances:
        if game and instance.nexus_slug != game:
            logger.trace(f"Nexus slug {instance.nexus_slug} does not match {game}.")
            continue

        startswith = (
            str(instance.instance_path).startswith(str(directory))
            if directory
            else False
        )
        if directory and not startswith:
            logger.trace(
                f"Instance path {instance.instance_path} does not start with {directory}."
            )
            continue

        if exact and directory and (instance.instance_path == directory):
            logger.trace(f"Matched instance at index {instance.index}: {instance}")
            matched.append(instance)
            continue
        elif (game == instance.nexus_slug) or (not exact and directory and startswith):
            logger.trace(f"Matched instance at index {instance.index}: {instance}")
            matched.append(instance)
            continue
        elif not exact and not (game or directory):
            logger.trace(
                f"Found existing instance at index {instance.index}: {instance}"
            )
            matched.append(instance)

    return matched


def symlink_instance():
    """
    Creates a symbolic link for the current instance's Mod Organizer 2 directory.
    """
    source = current_instance.instance_path
    target = Path("~/.config/mo2-lint/instances").expanduser() / str(
        current_instance.index
    )

    if not source.exists():
        logger.error(f"Source path {source} does not exist. Cannot create symlink.")
        return

    if target.exists() and target.is_symlink():
        symlink_correct = target.resolve() == source.resolve()
        if symlink_correct:
            logger.info(f"Symlink {target} already exists. Skipping creation.")
            return
        elif not symlink_correct:
            logger.warning(
                f"Symlink {target} points to a different location. Updating link."
            )
            target.unlink()
    elif target.exists() and not target.is_symlink():
        logger.warning(f"Path {target} exists and is not a symlink. Skipping creation.")
        logger.warning(
            "Please remove or relocate the existing path to create the symlink."
        )
        return

    target.symlink_to(source, target_is_directory=True)
