"""Regression checks for how the NXM handler forwards URLs to Mod Organizer 2."""

import importlib.util
import shlex
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

HANDLER_DIR = Path(__file__).resolve().parents[1] / "src/nxm-handler"


def load_handler():
    with patch.object(sys, "path", [str(HANDLER_DIR), *sys.path]):
        spec = importlib.util.spec_from_file_location(
            "nxm_handler_test", HANDLER_DIR / "__init__.py"
        )
        handler = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(handler)
    return handler


class NxmHandlerTests(unittest.TestCase):
    def test_steam_command_keeps_url_as_a_single_shell_argument(self):
        handler = load_handler()
        instance_dir = Path("/home/user/Games/mo2/it's here")
        for url in (
            "nxm://skyrimspecialedition/mods/1/files/2?key=abc&expires=1&user_id=3",
            "nxm://skyrimspecialedition/mods/1/files/2?k=x'; touch /tmp/pwned; '",
            'nxm://skyrimspecialedition/mods/1/files/2?k=$(id)`id`"\\',
        ):
            with patch.object(handler.protontricks, "run") as run:
                handler.send_url(
                    instance_dir,
                    url,
                    {"launcher": "steam", "steam_id": 489830},
                )
            option, command, app_id = run.call_args.args[0]
            self.assertEqual(option, "-c")
            self.assertEqual(app_id, "489830")
            self.assertEqual(
                shlex.split(command),
                ["wine", str(instance_dir / "nxmhandler.exe"), url],
            )


if __name__ == "__main__":
    unittest.main()
