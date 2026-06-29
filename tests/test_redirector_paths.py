#!/usr/bin/env python3

import json
import sys
from pathlib import Path
from unittest import TestCase, mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from redirector import game_dir_matches, get_instance_info, posix_to_wine, wine_io_path


class RedirectorPathTests(TestCase):
    def test_z_drive_state_path_uses_explicit_wine_path_under_wine(self):
        with mock.patch("redirector.os.name", "nt"):
            assert (
                str(wine_io_path("Z:/home/deck/.config/mo2-lint/state.json")).replace(
                    "\\", "/"
                )
                == "Z:/home/deck/.config/mo2-lint/state.json"
            )

    def test_z_drive_path_maps_to_posix_path_outside_wine(self):
        with mock.patch("redirector.os.name", "posix"):
            assert (
                str(wine_io_path("Z:/home/deck/.config/mo2-lint/state.json"))
                == "/home/deck/.config/mo2-lint/state.json"
            )

    def test_posix_to_wine_keeps_home_paths_on_z_drive(self):
        assert (
            posix_to_wine("/home/deck/Documents/mo2/ModOrganizer.exe")
            == r"Z:\home\deck\Documents\mo2\ModOrganizer.exe"
        )

    def test_game_dir_matches_normal_z_drive_launch(self):
        assert game_dir_matches(
            Path("/home/deck/.steam/steam/steamapps/common/Cyberpunk 2077"),
            Path("/home/deck/.steam/steam/steamapps/common/Cyberpunk 2077"),
        )

    def test_game_dir_matches_wine_z_drive_launch(self):
        assert game_dir_matches(
            Path("Z:/home/deck/.steam/steam/steamapps/common/Cyberpunk 2077"),
            Path("/home/deck/.steam/steam/steamapps/common/Cyberpunk 2077"),
        )

    def test_game_dir_matches_proton_game_drive_launch(self):
        assert game_dir_matches(
            Path("S:/common/Cyberpunk 2077"),
            Path("/home/deck/.steam/steam/steamapps/common/Cyberpunk 2077"),
        )

    def test_game_dir_matches_subdirectory_under_proton_game_drive(self):
        assert game_dir_matches(
            Path("S:/common/Cyberpunk 2077/bin/x64"),
            Path("/home/deck/.steam/steam/steamapps/common/Cyberpunk 2077"),
        )

    def test_game_dir_rejects_unrelated_game_drive_path(self):
        assert not game_dir_matches(
            Path("S:/common/Other Game"),
            Path("/home/deck/.steam/steam/steamapps/common/Cyberpunk 2077"),
        )

    def test_instance_paths_from_state_stay_on_z_drive_with_game_drive(self):
        state = {
            "instances": [
                {
                    "game_path": (
                        "/home/deck/.steam/steam/steamapps/common/Cyberpunk 2077"
                    ),
                    "instance_path": "/home/deck/Documents/mo2",
                    "game_executable": "bin/x64/Cyberpunk2077.exe",
                }
            ]
        }

        state_path = mock.Mock()
        state_path.is_file.return_value = True
        state_path.__fspath__ = lambda _: "/mock/state.json"

        with (
            mock.patch("redirector.wine_io_path", return_value=state_path),
            mock.patch("builtins.open", mock.mock_open(read_data=json.dumps(state))),
        ):
            mo2_exe, game_exe = get_instance_info(Path("S:/common/Cyberpunk 2077"))

        assert str(mo2_exe) == r"Z:\home\deck\Documents\mo2\ModOrganizer.exe"
        assert (
            game_exe == "/home/deck/.steam/steam/steamapps/common/Cyberpunk 2077/"
            "bin/x64/Cyberpunk2077.exe"
        )

    def test_instance_paths_from_state_stay_on_z_drive_with_z_drive(self):
        state = {
            "instances": [
                {
                    "game_path": (
                        "/home/deck/.steam/steam/steamapps/common/Cyberpunk 2077"
                    ),
                    "instance_path": "/home/deck/Documents/mo2",
                    "game_executable": "bin/x64/Cyberpunk2077.exe",
                }
            ]
        }

        state_path = mock.Mock()
        state_path.is_file.return_value = True
        state_path.__fspath__ = lambda _: "/mock/state.json"

        with (
            mock.patch("redirector.wine_io_path", return_value=state_path),
            mock.patch("builtins.open", mock.mock_open(read_data=json.dumps(state))),
        ):
            mo2_exe, game_exe = get_instance_info(
                Path("Z:/home/deck/.steam/steam/steamapps/common/Cyberpunk 2077")
            )

        assert str(mo2_exe) == r"Z:\home\deck\Documents\mo2\ModOrganizer.exe"
        assert (
            game_exe == "/home/deck/.steam/steam/steamapps/common/Cyberpunk 2077/"
            "bin/x64/Cyberpunk2077.exe"
        )
