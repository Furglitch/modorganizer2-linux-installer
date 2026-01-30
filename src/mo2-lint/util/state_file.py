#!/usr/bin/env python3

from dataclasses import dataclass, field
from loguru import logger
from pathlib import Path
from pydantic_core import from_json, to_json
from send2trash import send2trash
from shutil import move, rmtree
from typing import Optional
from util import variables as var, state_file as state
from uuid import UUID


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

    Raises
    ------
    TypeError
        If launcher_ids is not of type LauncherIDs.
    """

    index: int = None
    nexus_slug: str = None
    instance_path: Path = None
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
            nexus_slug=data.get("nexus_slug"),
            instance_path=Path(data.get("instance_path")),
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
            "nexus_slug": data.nexus_slug,
            "instance_path": str(data.instance_path),
            "launcher": data.launcher,
            "launcher_ids": var.LauncherIDs.to_dict(data.launcher_ids),
            "game_path": str(data.game_path),
            "game_executable": data.game_executable,
            "plugins": data.plugins,
        }

    def __post_init__(self):
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
                data = from_json(f.read())
        except Exception as e:
            logger.exception(
                f"Failed to parse state file JSON: {e}", backtrace=True, diagnose=True
            )
            logger.error("State file may be corrupted. Please validate or delete it.")
            logger.critical("Aborting...")
            SystemExit(1)
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
    game = var.input_params.game if not game else game
    directory = var.input_params.directory if not directory else directory
    if game is None and directory is None:
        logger.error("Either game or directory must be provided to check_instance.")
        raise ValueError("Either game or directory must be provided to check_instance.")
    logger.debug(
        f"Checking for instances with nexus slug: {game} or directory: {directory}"
    )
    global state_file, existing_indexes
    existing_indexes = []
    found_conflict = False
    for instance in state_file.instances:
        if (
            instance.instance_path == directory
            and instance.nexus_slug != game
            and not found_conflict
        ):
            found_conflict = True
            logger.warning(
                f"We've found an instance that matches this directory, but is not for the game {game}."
            )
            logger.warning(
                "Using this instance may lead to unexpected behavior. It is not recommended, and not supported."
            )
            logger.warning(
                "You have been warned. The script will proceed, but please be cautious when choosing this instance."
            )
        elif instance.instance_path == directory or instance.nexus_slug == game:
            logger.debug(
                f"Found matching instance at index {instance.index}: {instance}"
            )
        existing_indexes.append(instance)
    return None if existing_indexes == [] else existing_indexes


available_indexes: list[InstanceData] = []
current_instance: InstanceData = None


def choose_instance():
    """
    Prompts the user to choose between using an existing instance or creating a new one.
    """
    global current_instance, existing_indexes
    if existing_indexes:
        quantifier = "the" if len(existing_indexes) == 1 else "an"
        logger.debug("Prompting user to choose existing or new instance.")
        choice = (
            input(
                f"Would you like to use {quantifier} existing instance [e] or create a new one? [N]: "
            )
            .strip()
            .lower()
        )
        if choice.lower() == "e":
            logger.debug("User chose to use an existing instance.")
            if len(existing_indexes) == 1:
                logger.info(
                    "Only one existing instance found, selecting it automatically."
                )
                current_instance = existing_indexes[0]
            elif len(existing_indexes) > 1:
                for idx, inst in enumerate(existing_indexes, start=1):
                    print(
                        f"    - [{idx}] Game: {inst.nexus_slug}, Path: {inst.instance_path}, Script Extender: {'Yes' if inst.script_extender else 'No'}, Plugins: {', '.join(inst.plugins) if inst.plugins else 'None'}"
                    )
                selected = int(
                    input("Select the number of the instance you want to use: ")
                )
                current_instance = existing_indexes[selected - 1]

            if (
                current_instance.instance_path == var.input_params.directory
                and current_instance.nexus_slug != var.input_params.game
            ):
                (var.input_params.directory / ".conflict").touch(
                    exist_ok=True
                )  # if choice is a conflicting directory, put an empty file within to identify it
                logger.trace(
                    f"Created conflict file in {var.input_params.directory} to identify conflicting instance."
                )
        return
    set_index()


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
            permanent = (
                input("Move instance to trash [t] or delete permanently [d]? :")
                .strip()
                .lower()
                == "d"
            )
            if permanent:
                rmtree(instance_path)
            else:
                send2trash(instance_path)

        # Restore game executable if it was backed up
        game_exec = instance.game_path / instance.game_executable
        if game_exec.exists():
            rmtree(game_exec.parent / "modorganizer2")
            backup_exec = game_exec.with_suffix(".exe.bak")
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


def write_state(add_current: bool = True):
    global state_file, current_instance
    if {} in state_file.instances:
        logger.info("Removing empty instance entries from state file.")
        state_file.instances.remove({})
    if add_current and current_instance not in state_file.instances:
        logger.info(f"Adding current instance {current_instance.index} to state file.")
        state_file.instances.append(state.InstanceData.from_dict(current_instance))
    elif add_current and current_instance in state_file.instances:
        logger.info(
            f"Updating current instance {current_instance.index} in state file."
        )
        for i, inst in enumerate(state_file.instances):
            if inst.index == current_instance.index:
                state_file.instances[i] = state.InstanceData.from_dict(current_instance)

    json = to_json(StateFile.to_dict(state_file), indent=2)
    with filepath.open("w", encoding="utf-8") as f:
        f.write(json)
    logger.debug(f"Wrote state file with {len(state_file.instances)} instances.")


def match_instances(game: Optional[str], directory: Optional[Path]) -> dict:
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

    process = "Matching" if (game or directory) else "Existing"
    logger.debug(f"{process} Mod Organizer 2 Instances:")
    if not state_file.instances:
        logger.warning("No instances found that match the criteria.")
        return

    for instance in state_file.instances:
        if game and instance.nexus_slug != game:
            logger.trace(f"Nexus slug {instance.nexus_slug} does not match {game}.")
            continue
        if directory and not str(instance.instance_path).startswith(str(directory)):
            logger.trace(
                f"Instance path {instance.instance_path} does not start with {directory}."
            )
            continue

        if (game == instance.nexus_slug) or (
            str(instance.instance_path).startswith(str(directory))
        ):
            logger.trace(f"Matched instance at index {instance.index}: {instance}")
            matched.append(instance)
            continue

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
