#!/usr/bin/env python3
"""
Let protontricks drive ARM64 builds of Proton, as used on ARM64 Linux machines
such as the Valve Steam Frame.

protontricks (1.14) expects Proton's Wine binaries in ``files/bin``. ARM64 Proton
builds ship them in ``files/bin-arm64`` instead, and have no ``files/bin``, so
protontricks fails while listing that directory. ``apply()`` points protontricks
at a cache directory that mirrors Proton's ``files`` directory with symlinks,
mapping ``bin`` to ``bin-arm64``. Nothing inside the Proton installation itself
is changed, and x86_64 Proton builds are left alone.

On those machines Steam also exports ``STEAM_RUNTIME`` pointing at the legacy
x86 ``ubuntu12_32/steam-runtime``, which doesn't exist there; protontricks then
refuses to start. ``sanitize_environment()`` falls back to protontricks' own
runtime detection in that case.
"""

import os
from collections.abc import MutableMapping
from pathlib import Path


def sanitize_environment(env: MutableMapping[str, str]) -> None:
    """Drop a STEAM_RUNTIME path that doesn't exist (protontricks aborts on it)."""
    value = env.get("STEAM_RUNTIME", "")
    if value not in ("", "0", "1") and not Path(value).is_dir():
        env["STEAM_RUNTIME"] = "1"


def _shadow_dir(dist: Path, name: str) -> Path:
    cache = Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache")
    shadow = cache / "mo2-lint" / "protontricks-arm64" / name
    shadow.mkdir(parents=True, exist_ok=True)
    wanted = {
        ("bin" if entry.name == "bin-arm64" else entry.name): entry
        for entry in dist.iterdir()
    }
    for link in shadow.iterdir():
        if link.is_symlink() and wanted.get(link.name) != link.readlink():
            link.unlink(missing_ok=True)
    for link_name, target in wanted.items():
        link = shadow / link_name
        if not link.is_symlink():
            try:
                link.symlink_to(target)
            except FileExistsError:
                # Another process may have just created the same shadow link.
                if not link.is_symlink() or link.readlink() != target:
                    raise
    return shadow


def apply() -> None:
    """Patch protontricks (once per process) to handle ARM64 Proton builds."""
    from protontricks import steam

    if getattr(steam.SteamApp, "_mo2_lint_arm64", False):
        return
    original = steam.SteamApp.proton_dist_path

    def proton_dist_path(self):
        dist = original.fget(self)
        if dist is None or (dist / "bin").exists() or not (dist / "bin-arm64").is_dir():
            return dist
        return _shadow_dir(dist, self.name)

    steam.SteamApp.proton_dist_path = property(proton_dist_path)
    steam.SteamApp._mo2_lint_arm64 = True
