import os
from pathlib import Path

import vdf
from loguru import logger

STEAM_DIRS = [
    "~/.local/share/Steam",
    "~/.var/app/com.valvesoftware.Steam/.local/share/Steam",
    "~/snap/steam/common/.local/share/Steam",
    "~/.steam/steam",
    "~/.steam/root",
]


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


def _normalize_steam_library_path(path: str | Path) -> Path:
    path = Path(str(path)).expanduser()
    if str(path).endswith("/steamapps/common"):
        path = path.parent.parent
    elif str(path).endswith("/steamapps"):
        path = path.parent
    return path.resolve(strict=False)


def read_libraryfolders(root: Path) -> list[Path]:
    library_list = root / "steamapps" / "libraryfolders.vdf"
    if not library_list.exists():
        return []

    try:
        with open(library_list, "r", encoding="utf-8") as file:
            data = vdf.load(file)
    except Exception:
        logger.trace(f"Could not parse libraryfolders.vdf in {root}")
        return []

    libraries: list[Path] = []
    for entry in data.get("libraryfolders", {}).values():
        library_path = entry.get("path")
        if library_path:
            libraries.append(_normalize_steam_library_path(library_path))
    return list(dict.fromkeys(libraries))


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

    for candidate in STEAM_DIRS:
        root = resolve_steam_installation(candidate)
        if not root:
            continue

        for library in read_libraryfolders(root):
            if resolve_steam_installation(library):
                steam_installations.add(library)
                logger.debug(
                    f"Preferred Steam installation from libraryfolders.vdf: {library}"
                )

        steam_installations.add(root)
        logger.debug(f"Found Steam installation {root}")

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


def find_steam_libraries() -> list[Path]:
    root = find_steam_root()
    if not root:
        return []

    library = root if (root / "steamapps").exists() else root / "steam"
    library_list = root / "steamapps" / "libraryfolders.vdf"
    if not library_list.exists():
        logger.trace(
            f"libraryfolders.vdf not found in {library}, skipping this directory."
        )
        return []

    libraries = read_libraryfolders(root)
    if libraries:
        return libraries
    return []


def resolve_appinfo_vdf() -> Path:
    # TODO: Do we want to search all the possible roots for an appinfo and risk having different sections of the app disagree on the root? Should probably just use find_steam_root instead to ensure consistency. Could move checking for appcache/appinfo.vdf to find_steam_installations.
    steam_roots = find_steam_libraries()

    for root in steam_roots:
        appinfo_path = root.expanduser() / "appcache" / "appinfo.vdf"
        if appinfo_path.exists():
            return appinfo_path

    if steam_roots:
        return steam_roots[0].expanduser() / "appcache" / "appinfo.vdf"

    return Path("~/.steam/steam").expanduser() / "appcache" / "appinfo.vdf"
