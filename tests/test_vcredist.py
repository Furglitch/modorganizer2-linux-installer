"""Offline checks for VC++ runtime verification and repair.

Run with PYTHONPATH=src/mo2-lint:src python -m unittest discover -s tests.
"""

import shutil
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from step import configure_prefix as cp

CACHE = Path.home() / ".cache" / "mo2-lint" / "downloads" / "vcredist"


def wine_dll(path: Path, tag: bytes = b"Wine builtin DLL"):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"MZ" + b"\0" * 0x3E + tag + b"\0" * 64)


def native_dll(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"MZ" + b"\0" * 0x3E + b"This program cannot" + b"\0" * 64)


class VcredistTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def make_prefix(self, *, proton=True, win64=True) -> Path:
        base = self.root / "compatdata" / "489830"
        pfx = base / "pfx" if proton else base
        windows = pfx / "drive_c" / "windows"
        (windows / "system32").mkdir(parents=True)
        if win64:
            (windows / "syswow64").mkdir()
        return base

    def test_system_dll_dir_resolves_proton_and_wine_layouts(self):
        base = self.make_prefix(proton=True)
        windows = base / "pfx" / "drive_c" / "windows"
        self.assertEqual(cp._system_dll_dir(base, "x86"), windows / "syswow64")
        self.assertEqual(cp._system_dll_dir(base, "x64"), windows / "system32")
        # get_prefix() returns the pfx directory itself.
        self.assertEqual(cp._system_dll_dir(base / "pfx", "x64"), windows / "system32")

    def test_system_dll_dir_handles_win32_and_missing_prefix(self):
        base = self.make_prefix(proton=False, win64=False)
        self.assertEqual(
            cp._system_dll_dir(base, "x86"), base / "drive_c" / "windows" / "system32"
        )
        self.assertIsNone(cp._system_dll_dir(base, "x64"))
        self.assertIsNone(cp._system_dll_dir(self.root / "nope", "x86"))

    def test_builtin_detection_matches_proton(self):
        wine_dll(self.root / "a.dll")
        wine_dll(self.root / "b.dll", b"Wine placeholder DLL")
        native_dll(self.root / "c.dll")
        self.assertTrue(cp._is_wine_builtin(self.root / "a.dll"))
        self.assertTrue(cp._is_wine_builtin(self.root / "b.dll"))
        self.assertFalse(cp._is_wine_builtin(self.root / "c.dll"))
        self.assertFalse(cp._is_wine_builtin(self.root / "missing.dll"))

    def test_non_native_lists_builtin_and_missing_but_not_x64_only_on_x86(self):
        system = self.root / "sys"
        for dll in cp.vcrun_dlls:
            native_dll(system / f"{dll}.dll")
        wine_dll(system / "msvcp140.dll")
        (system / "vcruntime140.dll").unlink()
        (system / "vcruntime140_1.dll").unlink()
        self.assertEqual(
            cp._non_native_vcrun_dlls(system, "x86"), ["msvcp140", "vcruntime140"]
        )
        self.assertEqual(
            cp._non_native_vcrun_dlls(system, "x64"),
            ["msvcp140", "vcruntime140", "vcruntime140_1"],
        )

    def test_repair_skips_extraction_when_already_native(self):
        base = self.make_prefix()
        windows = base / "pfx" / "drive_c" / "windows"
        for dll in cp.vcrun_dlls:
            native_dll(windows / "system32" / f"{dll}.dll")
            native_dll(windows / "syswow64" / f"{dll}.dll")
        with patch.object(cp, "_download_vcredist") as download:
            self.assertTrue(cp.repair_vcredist_dlls(base))
        download.assert_not_called()

    def test_repair_reports_failure_without_cabextract(self):
        base = self.make_prefix()
        installer = self.root / "VC_redist.exe"
        installer.write_bytes(b"x")
        game_info = SimpleNamespace(launcher_ids=SimpleNamespace(steam=489830))
        with (
            patch.object(cp, "_download_vcredist", return_value=installer),
            patch.object(cp.shutil, "which", return_value=None),
            patch.object(cp.var, "game_info", game_info),
        ):
            self.assertFalse(cp.repair_vcredist_dlls(base))

    def test_extraction_never_writes_through_symlinked_builtins(self):
        if (
            not shutil.which("cabextract")
            or not (CACHE / "VC_redist.x64.exe").is_file()
        ):
            self.skipTest("needs cabextract and a cached VC_redist.x64.exe")
        proton_builtin = self.root / "proton" / "msvcp140.dll"
        wine_dll(proton_builtin)
        system = self.root / "system32"
        system.mkdir()
        (system / "msvcp140.dll").symlink_to(proton_builtin)

        remaining = cp._extract_vcrun_dlls(
            CACHE / "VC_redist.x64.exe", "x64", system, ["msvcp140"]
        )
        self.assertEqual(remaining, [])
        self.assertFalse((system / "msvcp140.dll").is_symlink())
        self.assertFalse(cp._is_wine_builtin(system / "msvcp140.dll"))
        self.assertTrue(cp._is_wine_builtin(proton_builtin))

    def test_extracts_every_runtime_dll_from_real_redistributables(self):
        missing = [
            a for a in ("x86", "x64") if not (CACHE / f"VC_redist.{a}.exe").is_file()
        ]
        if not shutil.which("cabextract") or missing:
            self.skipTest("needs cabextract and cached VC_redist installers")
        base = self.make_prefix()
        windows = base / "pfx" / "drive_c" / "windows"
        for dll in cp.vcrun_dlls:
            wine_dll(windows / "system32" / f"{dll}.dll")
            wine_dll(windows / "syswow64" / f"{dll}.dll")

        def cached(arch, _key):
            return CACHE / f"VC_redist.{arch}.exe"

        with patch.object(cp, "_download_vcredist", side_effect=cached):
            self.assertTrue(cp.repair_vcredist_dlls(base))
        self.assertEqual(cp._non_native_vcrun_dlls(windows / "system32", "x64"), [])
        self.assertEqual(cp._non_native_vcrun_dlls(windows / "syswow64", "x86"), [])


if __name__ == "__main__":
    unittest.main()
