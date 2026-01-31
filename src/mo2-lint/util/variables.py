#!/usr/bin/env python3

from dataclasses import dataclass, field
from loguru import logger
from pathlib import Path
from pydantic_core import from_json
from typing import Final
from typing import Optional, Tuple


@dataclass
class Input:
    """
    Stores command-line parameters

    Parameters
    -----------
    game : str
        Identifier for the game to set up MO2 for.
    directory: Path
        Path to the MO2 installation directory.
    game_info_path: Path, optional
        Path to custom game_info JSON file.
    log_level: str, optional
        Terminal log level.
    script_extender: bool, optional
        Whether to install a script extender.
    plugins: Tuple[str, ...], optional
        Plugin identifiers to install.

    Raises
    -------
    ValueError
        If required parameters [game, directory] are not provided
    """

    game: str = None
    directory: Path = None
    game_info_path: Optional[Path] = None
    log_level: Optional[str] = "INFO"
    script_extender: Optional[bool] = None
    plugins: Optional[Tuple[str, ...]] = field(default_factory=tuple)

    def __post_init__(self):
        if not self.game:
            raise ValueError("Input game must be provided.")
        if not self.directory:
            raise ValueError("Input directory must be provided.")


input_params: Input = None


def set_parameters(args: Input | dict):
    """
    Stores the command-line arguments for the application.

    Parameters
    -----------
    args : Input | dict
        Command-line arguments. See Input class for keys.
    """
    logger.debug(f"Setting input parameters: {args}")
    global input_params
    if isinstance(args, dict):
        input_params = Input(**args)
    elif isinstance(args, Input):
        input_params = args


@dataclass
class ScriptExtender:
    """
    Stores information about a specific script extender version.

    Parameters
    -----------
    version : str
        Version of the script extender.
    runtime : str, optional
        Target game runtime version required for this script extender.
    download_url : str, optional
        Direct download URL for the script extender.
    nexus_mod_id : int, optional
        Nexus Mods mod ID for the script extender.
    nexus_file_id : int, optional
        Nexus Mods file ID for the script extender.
    checksum : str, optional
        SHA-256 checksum of the script extender file.
    file_whitelist : Tuple[str, ...], optional
        File paths that should be included when installing the script extender. If not provided, all files will be installed.

    Raises
    -------
    ValueError
        If required parameters [version, (download_url or [nexus_mod_id, nexus_file_id])] are not provided
    """

    version: str = None
    runtime: Optional[str] = None
    download_url: Optional[str] = None
    nexus_mod_id: Optional[int] = None
    nexus_file_id: Optional[int] = None
    checksum: Optional[str] = None
    file_whitelist: Optional[Tuple[str, ...]] = field(default_factory=tuple)

    @classmethod
    def from_dict(cls, data: dict[str, any] | "ScriptExtender") -> "ScriptExtender":
        if isinstance(data, cls):
            return data
        return cls(
            version=data.get("version"),
            runtime=data.get("runtime") or None,
            download_url=data.get("download_url") or None,
            nexus_mod_id=data.get("nexus_mod_id") or None,
            nexus_file_id=data.get("nexus_file_id") or None,
            checksum=data.get("checksum") or None,
            file_whitelist=tuple(data.get("file_whitelist") or ()),
        )

    def __post_init__(self):
        if not self.version:
            raise ValueError("Script extender version must be provided.")
        if not (self.download_url or (self.nexus_mod_id and self.nexus_file_id)):
            raise ValueError(
                "Either download_url or both nexus_mod_id and nexus_file_id must be provided."
            )


@dataclass
class ScriptExtenders:
    """
    Stores ScriptExtender instances for different launchers.

    Parameters
    -----------
    epic : Tuple[ScriptExtender, ...], optional
        ScriptExtender instances for the Epic Games Store version.
    gog : Tuple[ScriptExtender, ...], optional
        ScriptExtender instances for the GOG.com version.
    steam : Tuple[ScriptExtender, ...], optional
        ScriptExtender instances for the Steam version.

    Raises
    -------
    ValueError
        If required parameters [(epic, gog, or steam)] are not provided
    """

    epic: Optional[Tuple[ScriptExtender, ...]] = None
    gog: Optional[Tuple[ScriptExtender, ...]] = None
    steam: Optional[Tuple[ScriptExtender, ...]] = None

    @classmethod
    def from_dict(cls, data: dict[str, any] | "ScriptExtenders") -> "ScriptExtenders":
        def make_tuple(key: str):
            if key is None:
                return tuple()
            if isinstance(key, dict):
                return (ScriptExtender.from_dict(key),)
            elif isinstance(key, list):
                return tuple(ScriptExtender.from_dict(item) for item in key)

        if isinstance(data, cls):
            return data
        return cls(
            epic=make_tuple(data.get("epic")) if data.get("epic") else tuple(),
            gog=make_tuple(data.get("gog")) if data.get("gog") else tuple(),
            steam=make_tuple(data.get("steam")) if data.get("steam") else tuple(),
        )

    def __post_init__(self):
        if not (self.epic or self.gog or self.steam):
            raise ValueError("Either epic, gog, or steam must be provided.")


@dataclass
class LauncherIDs:
    """
    Stores launcher-specific IDs for a game.

    Parameters
    -----------
    steam : int, optional
        Steam app ID for the game.
    gog : int, optional
        GOG ID for the game.
    epic : str, optional
        Epic Games Store ID for the game.

    Raises
    -------
    ValueError
        If none of the parameters [steam, gog, epic] are provided
    """

    steam: Optional[int] = None
    gog: Optional[int] = None
    epic: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict | "LauncherIDs") -> "LauncherIDs":
        if isinstance(data, cls):
            return data
        return cls(
            steam=data.get("steam") or None,
            gog=data.get("gog") or None,
            epic=data.get("epic") or None,
        )

    @classmethod
    def to_dict(cls, data: "LauncherIDs") -> dict[str, any]:
        return {
            "steam": data.steam,
            "gog": data.gog,
            "epic": data.epic,
        }

    def __post_init__(self):
        if not (self.steam or self.gog or self.epic):
            raise ValueError("At least one game ID must be provided.")


@dataclass
class GameInfo:
    """
    Stores data from the game_info.json file.

    Parameters
    -----------
    display_name : str
        Display name of the game, for use in logs and messages.
    nexus_slug : str
        Nexus Mods ID for the game.
    launcher_ids : LauncherIDs
        Contains launcher-specific IDs for the game.
    subdirectory : str, optional
        Root directory for the game, relative to Steam library folder.
    executable : str, optional
        Game executable filename.
    tricks : Tuple[str, ...], optional
        List of tricks to apply for the game.
    script_extenders : ScriptExtenders, optional
        Contains information about script extenders for the game.

    Raises
    -------
    ValueError
        If required parameters [display_name, nexus_slug, launcher_ids] are not provided
    """

    display_name: str = None
    nexus_slug: str = None
    launcher_ids: LauncherIDs = None
    subdirectory: Optional[str] = None
    executable: Optional[str] = None
    tricks: Optional[Tuple[str, ...]] = field(default_factory=tuple)
    script_extenders: Optional[ScriptExtenders] = None

    @classmethod
    def from_dict(cls, data: dict[str, any] | "GameInfo") -> "GameInfo":
        if isinstance(data, cls):
            return data
        return cls(
            display_name=data.get("display_name"),
            nexus_slug=data.get("nexus_slug"),
            launcher_ids=LauncherIDs.from_dict(data.get("launcher_ids")),
            subdirectory=data.get("subdirectory") or None,
            executable=data.get("executable") or None,
            tricks=tuple(data.get("tricks") or ()),
            script_extenders=ScriptExtenders.from_dict(data.get("script_extenders"))
            if data.get("script_extenders")
            else None,
        )

    def __post_init__(self):
        if not self.display_name:
            raise ValueError("Game display_name must be provided.")
        if not self.nexus_slug:
            raise ValueError("Game nexus_slug must be provided.")
        if not self.launcher_ids:
            raise ValueError("Game launcher_ids must be provided.")


game_info: dict[str, GameInfo] = {}


def load_game_info(path: Optional[Path] = None):
    """
    Loads information from a game_info.json file into the global game_info variable.

    Parameters
    -----------
    path : Path, optional
        Path to game_info JSON file. If not provided, defaults to the internal cfg/game_info.json file.
    """
    global game_info
    if not path:
        path = Path("~/.config/mo2-lint/game_info.json").expanduser()
    logger.debug(f"Loading game info from path: {path}")
    with open(path, "r", encoding="utf-8") as file:
        json = from_json(file.read())
    logger.trace(f"Game info JSON content: {json}")
    for key, value in json.items():
        game_info[key] = GameInfo.from_dict(value)


@dataclass
class Resource:
    """
    Stores information about a downloadable resource.

    Parameters
    -----------
    download_url : str
        Direct download URL for the resource.
    checksum : str, optional
        SHA-256 checksum of the resource file.
    internal_checksum : str, optional
        SHA-256 checksum of an internal file within the resource archive.
    version : str, optional
        Version string for the resource.

    Raises
    -------
    ValueError
        If required parameters [download_url, checksum] are not provided
    """

    download_url: str = None
    checksum: Optional[str] = None
    internal_checksum: Optional[str] = None
    version: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict[str, any] | "Resource") -> "Resource":
        if isinstance(data, cls):
            return data
        return cls(
            download_url=data.get("download_url"),
            version=data.get("version") if "version" in data else None,
            checksum=data.get("checksum"),
            internal_checksum=data.get("internal_checksum"),
        )

    def __post_init__(self):
        if not self.download_url:
            raise ValueError("Resource download_url is missing.")


@dataclass
class ResourceInfo:
    """
    Stores download information for various resources.

    Parameters
    -----------
    mod_organizer : Resource
        Resource instance for Mod Organizer.
    winetricks : Resource
        Resource instance for Winetricks.
    java : Resource, optional
        Resource instance for Java.

    Raises
    -------
    ValueError
        If required parameters [mod_organizer, winetricks] are not provided
    """

    mod_organizer: Resource = None
    winetricks: Resource = None
    java: Optional[Resource] = None

    @classmethod
    def from_dict(cls, data: dict[str, any] | "ResourceInfo") -> "ResourceInfo":
        if isinstance(data, cls):
            return data
        return cls(
            mod_organizer=Resource.from_dict(data.get("mod_organizer")),
            winetricks=Resource.from_dict(data.get("winetricks")),
            java=Resource.from_dict(data.get("java")) if data.get("java") else None,
        )

    def __post_init__(self):
        if not self.mod_organizer:
            raise ValueError("Mod Organizer resource info must be provided.")
        if not self.winetricks:
            raise ValueError("Winetricks resource info must be provided.")


resource_info: ResourceInfo = None


def load_resource_info(path: Optional[Path] = None):
    """
    Loads information from a resource_info.json file into global resource_info variable.

    Parameters
    -----------
    path : Path, optional
        Path to resource_info JSON file. If not provided, defaults to the internal cfg/resource_info.json file.
    """

    global resource_info
    if not path:
        path = Path("~/.config/mo2-lint/resource_info.json").expanduser()
    logger.debug(f"Loading resource info from path: {path}")
    with open(path, "r", encoding="utf-8") as file:
        json = from_json(file.read())
    logger.trace(f"Resource info JSON content: {json}")
    resource_info = ResourceInfo.from_dict(json)


@dataclass
class Plugin:
    """
    Stores information about a plugin

    Parameters
    -----------
    manifest : str
        Direct URL to plugin manifest file.\n
        Manifest is formatted using the Kezyma plugin manifest schema. More info: https://github.com/Kezyma/ModOrganizer-Plugins/blob/main/docs/pluginfinder.md#adding-your-plugin

    Raises
    -------
    ValueError
        If required parameters [manifest] are not provided
    """

    manifest: str = None

    def __post_init__(self):
        if not self.manifest:
            raise ValueError("Plugin manifest must be provided.")


plugin_info: dict[str, Plugin] = {}


def load_plugin_info(path: Optional[Path] = None):
    """
    Loads information from a plugin_info.json file into the global plugin_info variable.

    Parameters
    -----------
    path : Path, optional
        Path to plugin_info JSON file. If not provided, defaults to the internal cfg/plugin_info.json file.
    """

    global plugin_info
    if not path:
        path = Path("~/.config/mo2-lint/plugin_info.json").expanduser()
    logger.debug(f"Loading plugin info from path: {path}")
    with open(path, "r", encoding="utf-8") as file:
        json = from_json(file.read())  # type: list[dict]
    logger.trace(f"Plugin info JSON content: {json}")
    for value in json:
        plugin_info[value.get("identifier")] = Plugin(manifest=value.get("manifest"))


# --- #

version: Final = "7.0.0"
"""
Current version of mo2-lint.
"""

launcher: str = None
"""
Targeted launcher [steam, epic, gog].
"""

prefix: Path = None
"""
Path to game's Wine/Proton prefix directory.
"""

archived_prefix: Path = None
"""
Path to archived Wine/Proton prefix directory.
"""

archived_prefixes: list[Path] = []
"""
List of previously archived Wine/Proton prefix directories.
"""

heroic_config: tuple[str, str | int, Path, Path, Path] = ()

game_install_path: Path = None
"""
Path to the game's installation directory.
"""
