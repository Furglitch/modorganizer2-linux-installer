from pathlib import Path
from typing import Iterable

import vdf
from loguru import logger


# Check these files exist when searching for a Proton version
# NOTE: Consider adding other files required by protonttricks such as files/bin/wine
proton_files = {"proton", "toolmanifest.vdf"}


def looks_like_proton(proton_path: Path) -> bool:
    try:
        return all(proton_path.joinpath(name).exists() for name in proton_files)
    except Exception:
        logger.exception(
            f'Could not check if "{proton_path}" contains a Proton installation'
        )
        return False


def find_proton(libraries: Iterable[Path], proton_version: str) -> Path | None:
    for library_path in libraries:
        proton_path = library_path / "steamapps" / "common" / proton_version
        if looks_like_proton(proton_path):
            return proton_path
    return None


def read_require_tool_appid(proton_path: Path) -> str | None:
    try:
        with open(proton_path / "toolmanifest.vdf") as fp:
            manifest = vdf.load(fp)
    except Exception:
        logger.exception(
            "Could not parse toolmanifest.vdf to get the required_tool_version"
        )
        return None

    return manifest.get("manifest", {}).get("require_tool_appid", None)
