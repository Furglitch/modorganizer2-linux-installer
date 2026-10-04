"""Check bundled configuration and start the nxm-handler extracted from a frozen build."""

import subprocess
import sys
import tempfile
from pathlib import Path

from PyInstaller.archive.readers import CArchiveReader


def verify(binary: Path):
    archive = CArchiveReader(str(binary))
    for name in (
        "cfg/settings.toml",
        "cfg/game_info.yml",
        "cfg/resource_info.yml",
        "cfg/plugin_info.yml",
        "cfg/theme_info.yml",
        "dist/mo2-redirector.exe",
        "dist/nxm-handler",
    ):
        if not archive.extract(name):
            raise AssertionError(f"Missing or empty bundled file: {name}")
    with tempfile.TemporaryDirectory(prefix="mo2-lint-frozen-") as directory:
        handler = Path(directory) / "nxm-handler"
        handler.write_bytes(archive.extract("dist/nxm-handler"))
        handler.chmod(0o755)
        subprocess.run([str(handler), "--help"], check=True, timeout=30)
    print("Frozen configuration, redirector and nxm-handler startup verified.")


if __name__ == "__main__":
    verify(Path(sys.argv[1]))
