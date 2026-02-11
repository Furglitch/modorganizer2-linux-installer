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
        cls, data: "dict[str, any] | NexusAPIData"
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
            logger.warning("NexusAPIData: UUID is not set.")
        if not self.connection_token:
            logger.warning("NexusAPIData: Connection token is not set.")
        if not self.api_key:
            logger.warning("NexusAPIData: API key is not set.")


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
    def from_dict(cls, data: "dict[str, any] | InstanceData") -> "InstanceData":
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
        if not self.game:
            logger.warning("InstanceData: Game is not set.")
        elif self.game not in var.games_info.keys():
            logger.warning(
                f"InstanceData: Game '{self.game}' is not a valid game identifier."
            )
        if not self.nexus_slug:
            logger.warning("InstanceData: Nexus slug is not set.")
        if not self.instance_path:
            logger.warning("InstanceData: Instance path is not set.")
        if not self.launcher:
            logger.warning("InstanceData: Launcher is not set.")
        if not self.launcher_ids:
            logger.warning("InstanceData: Launcher IDs are not set.")
        if not self.game_path:
            logger.warning("InstanceData: Game install path is not set.")
        if not self.game_executable:
            logger.warning("InstanceData: Game executable is not set.")
        if self.plugins is None:
            self.plugins = []
        elif any(plugin not in var.plugin_info for plugin in self.plugins):
            logger.warning("InstanceData: One or more plugins are not recognized.")


@dataclass
class StateFile:
    """
    Represents the state file JSON storing MO2 instances and Nexus API data.
    """

    nexus_api: Optional[NexusAPIData] = None
    instances: list[InstanceData] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: "dict[str, any] | StateFile") -> "StateFile":
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
filepath = Path("~/.config/mo2-lint/state.json").expanduser()


def load_state_file():
    """
    Loads the state file from disk into the global state_file variable.
    If the file does not exist, initializes an empty StateFile.
    """
    global state_file
    if filepath.exists():
        logger.debug("Loading state file from disk.")
        try:
            with filepath.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            logger.exception(f"Failed to load state file: {e}")
            logger.critical(
                "State file is corrupted or unreadable. Please validate or delete it to continue."
            )
            raise SystemExit(1)
        state_file = StateFile.from_dict(data)
    else:
        logger.trace("State file does not exist. Initializing new state.")
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
    logger.trace("Calculating next available instance index.")
    for inst in state_file.instances:
        if inst.index and inst.index > max:
            max = inst.index
    set = max + 1
    logger.trace(f"Next available instance index calculated: {set}")
    if index:
        if index not in [inst.index for inst in state_file.instances]:
            set = index
            logger.trace(f"Assigned provided index {set} to current instance.")
        else:
            logger.warning(
                f"Provided index {index} is already in use. Assigning next available index instead."
            )
    else:
        logger.trace(
            f"No index provided. Assigned next available index {set} to current instance."
        )
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
            logger.success(
                f"Symlink for instance index {instance.index} removed successfully."
            )
        else:
            if symlink_path.exists():
                logger.warning(
                    f"Expected symlink path exists but is not a symlink: {symlink_path}"
                )
            else:
                logger.debug(
                    f"Symlink path for instance index {instance.index} does not exist, skipping removal."
                )

    if "install" in types:
        instance_path = instance.instance_path
        if instance_path.exists():
            if not lang.prompt_uninstall_trash():
                logger.debug(
                    f"User chose to send instance directory to trash: {instance_path}"
                )
                send2trash(instance_path)
                logger.success(f"Instance directory sent to trash: {instance_path}")
            else:
                logger.debug(
                    f"User chose to permanently delete instance directory: {instance_path}"
                )
                if lang.prompt_uninstall_trash_confirm():
                    logger.debug(
                        f"User confirmed permanent deletion of instance directory: {instance_path}"
                    )
                    rmtree(instance_path)
                    logger.success(
                        f"Instance directory permanently deleted: {instance_path}"
                    )
                else:
                    logger.debug(
                        f"User denied confirmation for permanent deletion of instance directory: {instance_path}; Sending to trash instead."
                    )
                    send2trash(instance_path)
                    logger.success(f"Instance directory sent to trash: {instance_path}")
        else:
            logger.trace(
                f"Instance directory for index {instance.index} does not exist, skipping removal."
            )

        # Restore game executable if it was backed up
        exec = (
            instance.game_executable.get(instance.launcher)
            if isinstance(instance.game_executable, dict)
            else instance.game_executable
        )
        game_exec = instance.game_path / exec
        if game_exec.exists():
            logger.trace(f"Game executable exists at expected path: {game_exec}")
            data_dir = game_exec.parent / "modorganizer2"
            if data_dir.exists() and data_dir.is_dir():
                rmtree(data_dir)
                logger.success(
                    f"Removed Redirector data directory from game path: {data_dir}"
                )

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
                logger.debug(f"Restored game executable from backup: {game_exec}")
            else:
                pass

    if "state" in types:
        global state_file
        state_file.instances = [
            inst for inst in state_file.instances if inst.index != instance.index
        ]
        logger.trace(f"Removed instance index {instance.index} from state file.")

    write_state(False)
    logger.trace(f"State file updated after removing instance index {instance.index}.")


def write_state(add_current: bool = True):
    global state_file, current_instance

    if {} in state_file.instances:
        logger.trace("Found empty instance entry in state file. Removing it.")
        state_file.instances.remove({})
    if add_current and current_instance.index not in [
        inst.index for inst in state_file.instances
    ]:
        logger.trace(f"Adding current instance to state file: {current_instance}")
        state_file.instances.append(state.InstanceData.from_dict(current_instance))
    elif add_current and current_instance.index in [
        inst.index for inst in state_file.instances
    ]:
        logger.trace(
            f"Updating existing instance in state file with index {current_instance.index}."
        )
        for i, inst in enumerate(state_file.instances):
            if inst.index == current_instance.index:
                state_file.instances[i] = state.InstanceData.from_dict(current_instance)

    json = to_json(StateFile.to_dict(state_file), indent=2).decode("utf-8")
    with filepath.open("w", encoding="utf-8") as f:
        f.write(json)
    logger.success(f"State file written to disk at: {filepath}")


def match_instances(
    game: Optional[str] = None, directory: Optional[Path] = None, exact: bool = False
) -> list[InstanceData]:
    """
    Matches instances in the state_file based on the provided game or directory.

    Parameters
    ----------
    game : str, optional
        Nexus Mods slug identifier for the game to match.
    directory : Path, optional
        Directory path to match instances against.
    exact : bool, optional
        If True, requires an exact match for the directory. If False, matches any instance whose directory starts with the given directory.

    Returns
    -------
    list[InstanceData]
        A list of matched instances.
    """

    global state_file
    matched: list[InstanceData] = []

    if not state_file.instances:
        logger.debug("No instances found in state file.")
        return []

    if not (game or directory):
        logger.debug("No game or directory criteria provided. Returning all instances.")

    for instance in state_file.instances:
        if game and instance.nexus_slug != game:
            logger.trace(
                f"Instance index {instance.index} does not match game slug '{game}'. Skipping."
            )
            continue

        startswith = (
            str(instance.instance_path).startswith(str(directory))
            if directory
            else False
        )
        if directory and not startswith:
            logger.trace(
                f"Instance index {instance.index} does not match directory '{directory}'. Skipping."
            )
            continue

        if exact and directory and (instance.instance_path == directory):
            logger.trace(
                f"Instance index {instance.index} matches directory '{directory}' exactly. Adding to matched list."
            )
            matched.append(instance)
            continue
        elif (game == instance.nexus_slug) or (not exact and directory and startswith):
            logger.trace(
                f"Instance index {instance.index} matches criteria (game: '{game}', directory: '{directory}'). Adding to matched list."
            )
            matched.append(instance)
            continue
        elif not exact and not (game or directory):
            logger.trace(f"Adding instance index {instance.index} to matched list.")
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
        logger.error(
            f"Cannot create symlink: Source instance path does not exist: {source}"
        )
        return

    if target.exists() and target.is_symlink():
        symlink_correct = target.resolve() == source.resolve()
        if symlink_correct:
            logger.debug(
                f"Symlink for instance index {current_instance.index} already exists and is correct. No action needed."
            )
            return
        elif not symlink_correct:
            logger.warning(
                f"Symlink for instance index {current_instance.index} exists but points to a different location. Removing incorrect symlink."
            )
            target.unlink()
    elif target.exists() and not target.is_symlink():
        logger.warning(
            f"Expected symlink path exists but is not a symlink: {target}. Aborting symlink creation to avoid overwriting."
        )
        return

    target.symlink_to(source, target_is_directory=True)
    logger.debug(
        f"Created symlink for instance index {current_instance.index}: {target} -> {source}"
    )
