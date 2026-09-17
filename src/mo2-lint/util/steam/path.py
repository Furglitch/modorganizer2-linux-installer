import os
from pathlib import Path

from loguru import logger

from util.steam.find_library import steam_directories, get_libraries


class OrderedSet[T]:
    def __init__(self):
        self.keys: set[T] = set()
        self.items: list[T] = []

    def add(self, item: T):
        if item not in self:
            self.keys.add(item)
            self.items.append(item)

    def __getitem__(self, index: int):
        return self.items[index]

    def __contains__(self, item: T):
        return item in self.keys

    def __iter__(self):
        return iter(self.items)

    def __len__(self) -> int:
        return len(self.items)

    def __str__(self) -> str:
        return str(self.items)


def resolve_steam_installation(path: Path | str) -> Path | None:
    def has_steamapps_dir(path: Path) -> bool:
        return (path / "steamapps").is_dir()

    def has_runtime_dir(path: Path) -> bool:
        return (path / "ubuntu12_32").is_dir()

    def is_steam_root(path: Path) -> bool:
        # follow the same logic as protontricks
        return has_steamapps_dir(path) and has_runtime_dir(path)

    path = Path(path).expanduser().resolve()
    if is_steam_root(path):
        return path
    else:
        return None


def find_steam_installations() -> list[Path]:
    path = os.getenv("STEAM_DIR")
    if path:
        path = resolve_steam_installation(path)
        if path:
            logger.info(f"Using Steam root from STEAM_DIR: {path}")
            return [path]
        else:
            logger.error(
                "STEAM_DIR was provided but did not point to a valid Steam installation"
            )
            return []

    steam_installations: OrderedSet[Path] = OrderedSet()
    for candidate in steam_directories:
        path = resolve_steam_installation(candidate)
        if path:
            steam_installations.add(path)
            logger.debug(f"Found Steam installation {path}")
        else:
            logger.trace(f"Not a valid Steam installation {candidate}")

    return steam_installations.items


def find_steam_root() -> Path | None:
    steam_installations = find_steam_installations()
    if not steam_installations:
        return None

    if len(steam_installations) > 1:
        logger.warning(
            "Found multiple Steam directories. If you want to select a "
            "specific installation, use STEAM_DIR environment variable to set "
            "the correct directory"
        )

    return steam_installations[0]


def resolve_appinfo_vdf() -> Path:
    # TODO: Do we want to search all the possible roots for an appinfo and risk having different sections of the app disagree on the root? Should probably just use find_steam_root instead to ensure consistency. Could move checking for appcache/appinfo.vdf to find_steam_installations.
    steam_roots = get_libraries()

    for root in steam_roots:
        appinfo_path = root.expanduser() / "appcache" / "appinfo.vdf"
        if appinfo_path.exists():
            return appinfo_path

    if steam_roots:
        return steam_roots[0].expanduser() / "appcache" / "appinfo.vdf"

    return Path("~/.steam/steam").expanduser() / "appcache" / "appinfo.vdf"
