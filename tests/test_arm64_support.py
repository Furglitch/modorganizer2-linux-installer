"""Regression checks for ARM64 Proton compatibility without modifying Proton."""

import importlib.util
import os
import tempfile
import unittest
from contextlib import nullcontext
from pathlib import Path
from unittest.mock import patch

from protontricks import steam

from shared import host, protontricks_arm64


class Arm64SupportTests(unittest.TestCase):
    def test_missing_runtime_path_falls_back_but_valid_controls_survive(self):
        with tempfile.TemporaryDirectory() as directory:
            for original, expected in (
                (directory, directory),
                ("0", "0"),
                ("1", "1"),
                ("", ""),
                (directory + "/absent", "1"),
            ):
                env = {"STEAM_RUNTIME": original, "OTHER": "unchanged"}
                protontricks_arm64.sanitize_environment(env)
                self.assertEqual(env, {"STEAM_RUNTIME": expected, "OTHER": "unchanged"})

    def test_frame_detection_handles_quoted_values_and_missing_os_release(self):
        for text, expected in (
            ('ID=steamos\nVARIANT_ID="vr"\n', True),
            ("VARIANT_ID=steamdeck\n", False),
            ("ID=arch\n", False),
            ("ID=another-distro\nVARIANT_ID=vr\n", False),
            ("VARIANT_ID=vr\n", False),
        ):
            with patch.object(Path, "read_text", return_value=text):
                self.assertEqual(host.is_steam_frame(), expected)
        with patch.object(Path, "read_text", side_effect=OSError):
            self.assertFalse(host.is_steam_frame())

    def test_proton_shadow_updates_links_without_changing_either_installation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first, second = root / "first", root / "second"
            for dist in (first, second):
                (dist / "bin-arm64").mkdir(parents=True)
                (dist / "lib").mkdir()
            (first / "old-file").touch()
            with patch.dict(os.environ, {"XDG_CACHE_HOME": str(root / "cache")}):
                shadow = protontricks_arm64._shadow_dir(first, "Proton 11.0 (ARM64)")
                self.assertEqual((shadow / "bin").resolve(), first / "bin-arm64")
                refreshed = protontricks_arm64._shadow_dir(
                    second, "Proton 11.0 (ARM64)"
                )
                self.assertEqual(refreshed, shadow)
                self.assertEqual((shadow / "bin").resolve(), second / "bin-arm64")
                self.assertFalse((shadow / "old-file").exists())
            self.assertFalse((first / "bin").exists())
            self.assertFalse((second / "bin").exists())

    def test_patch_is_idempotent_and_leaves_x86_proton_unchanged(self):
        class FakeSteamApp:
            def __init__(self, dist):
                self.dist = dist
                self.name = "Proton"

            @property
            def proton_dist_path(self):
                return self.dist

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            x86, arm = root / "x86", root / "arm"
            (x86 / "bin").mkdir(parents=True)
            (arm / "bin-arm64").mkdir(parents=True)
            with (
                patch.object(steam, "SteamApp", FakeSteamApp),
                patch.dict(os.environ, {"XDG_CACHE_HOME": str(root / "cache")}),
            ):
                protontricks_arm64.apply()
                first_property = FakeSteamApp.proton_dist_path
                protontricks_arm64.apply()
                self.assertIs(FakeSteamApp.proton_dist_path, first_property)
                self.assertEqual(FakeSteamApp(x86).proton_dist_path, x86)
                self.assertIsNone(FakeSteamApp(None).proton_dist_path)
                shadow = FakeSteamApp(arm).proton_dist_path
                self.assertEqual((shadow / "bin").resolve(), arm / "bin-arm64")
                self.assertFalse((arm / "bin").exists())

    def test_architecture_aliases_use_one_canonical_name(self):
        for reported, expected in (
            ("amd64", "x86_64"),
            ("x86_64", "x86_64"),
            ("arm64", "aarch64"),
            ("aarch64", "aarch64"),
            ("riscv64", "riscv64"),
        ):
            with patch.object(host.platform, "machine", return_value=reported):
                self.assertEqual(host.machine(), expected)
                self.assertEqual(host.is_x86_64(), expected == "x86_64")
                self.assertEqual(host.is_arm64(), expected == "aarch64")

    def test_concurrent_shadow_link_creation_accepts_the_same_target(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            dist = root / "proton"
            (dist / "bin-arm64").mkdir(parents=True)
            original = Path.symlink_to

            def concurrent_create(link, target, *args, **kwargs):
                original(link, target, *args, **kwargs)
                raise FileExistsError("another process created the same link")

            with (
                patch.dict(os.environ, {"XDG_CACHE_HOME": str(root / "cache")}),
                patch.object(Path, "symlink_to", concurrent_create),
            ):
                shadow = protontricks_arm64._shadow_dir(dist, "Proton")
            self.assertEqual((shadow / "bin").resolve(), dist / "bin-arm64")

    def test_nxm_handler_restores_runtime_after_success_and_failure(self):
        path = (
            Path(__file__).resolve().parents[1] / "src/nxm-handler/protontricks_util.py"
        )
        spec = importlib.util.spec_from_file_location("nxm_protontricks_test", path)
        handler = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(handler)
        for overrides, expected, fail in (
            (None, "1", False),
            ({"STEAM_RUNTIME": "/missing-caller-runtime"}, "1", True),
            ({"STEAM_RUNTIME": None}, None, False),
        ):

            def protontricks(args, expected=expected, fail=fail):
                self.assertEqual(os.environ.get("STEAM_RUNTIME"), expected)
                if fail:
                    raise SystemExit(1)

            with (
                patch.dict(os.environ, {"STEAM_RUNTIME": "/missing-host-runtime"}),
                patch.object(
                    handler, "redirect_output_to_logger", return_value=nullcontext([])
                ),
                patch.object(handler, "pt", side_effect=protontricks),
                patch.object(protontricks_arm64, "apply"),
            ):
                handler.run(["--version"], env=overrides)
                self.assertEqual(os.environ["STEAM_RUNTIME"], "/missing-host-runtime")


if __name__ == "__main__":
    unittest.main()
