#!usr/bin/env python3

from pathlib import Path
from typing import Optional
import click
from util import variables as var, state_file as state
from util.state_file import set_index, InstanceData
from util.redirector.install import install as install_redirector
from util.nexus.install_handler import install as install_handler
from step.workarounds import apply_workarounds
from step.load_game_info import get_launcher, get_library
from step.external_resources import download
from step.configure_prefix import prompt as prompt_prefix, configure as configure_prefix


def install(
    game: str,
    directory: Path,
    game_info_path: Optional[Path] = None,
    log_level: str = "INFO",
    script_extender: bool = False,
    plugin: Optional[list] = [],
    plugin_list: Optional[str] = None,
):
    if plugin:
        for p in plugin:
            if p not in var.plugin_info:
                raise click.BadArgumentUsage(
                    f"Invalid plugin specified: {p}. Available plugins are: {plugin_list}"
                )

    var.set_parameters(
        {
            "game": game,
            "directory": directory,
            "game_info_path": game_info_path,
            "log_level": log_level,
            "script_extender": script_extender,
            "plugins": list(plugin),
        }
    )
    directory.mkdir(parents=True, exist_ok=True)

    if state.check_instance(game, str(directory)):
        state.choose_instance()
    else:
        state.current_instance = InstanceData(
            index=-1,
            nexus_slug=game,
            instance_path=directory,
            launcher=get_launcher(),
            launcher_ids=var.LauncherIDs.from_dict(var.game_info.launcher_ids),
            game_path=get_library(),
            game_executable=var.game_info.executable,
            script_extender=script_extender,
            plugins=list(plugin),
        )
        set_index()

    prompt_prefix()
    configure_prefix()
    download()
    install_handler()
    install_redirector()
    apply_workarounds()
