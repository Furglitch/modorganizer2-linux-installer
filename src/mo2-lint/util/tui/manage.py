from textual.app import Screen, ComposeResult
from textual.containers import HorizontalGroup, VerticalGroup
from textual.widgets import (
    Button,
    Header,
    Footer,
    Markdown,
    OptionList,
)
from .. import state_file as state

INSTANCE_INFO = """
Game: _GAME\n
MO2 Path: _MO2\n
Game Path: _PATH\n
Pinned: _PIN\n
Launcher: _LAUNCHER\n
Script Extender: _SE\n
Plugins: _PLUGINS\n
"""


class ManageInstance(Screen):
    # TITLE = "MO2-LINT v" + var.version
    SUB_TITLE = "Manage Instances"

    def compose(self) -> ComposeResult:
        yield Header()
        yield self.Instances()
        yield Footer()

    class Instances(HorizontalGroup):
        instance_list = [
            str(instance.display_name) for instance in state.state_file.instances
        ]
        info = Markdown(INSTANCE_INFO, id="manageinstanceinfo")

        def compose(self) -> ComposeResult:
            instances = OptionList(*self.instance_list, id="manageinstancelist")
            instances.border_title = "Instances"
            yield instances
            yield self.info
            yield self.ManageChoices()

        class ManageChoices(VerticalGroup):
            def compose(self) -> ComposeResult:
                yield Button("Update", id="manageinstanceupdate")
                yield Button("Pin", id="manageinstancepin")
                yield Button("Uninstall", id="manageinstanceuninstall")

    def on_option_list_option_highlighted(
        self, event: OptionList.OptionHighlighted
    ) -> None:
        if event.option_list.id == "manageinstancelist":
            game_info = INSTANCE_INFO
            instance = state.state_file.instances[event.option_index]
            game_info = game_info.replace("_GAME", str(instance.game))
            game_info = game_info.replace("_MO2", str(instance.instance_path))
            game_info = game_info.replace("_PATH", str(instance.game_path))
            game_info = game_info.replace("_PIN", ("Yes" if instance.pin else "No"))
            game_info = game_info.replace("_LAUNCHER", str(instance.launcher))
            game_info = game_info.replace(
                "_SE",
                str(instance.script_extender) if instance.script_extender else "None",
            )
            game_info = game_info.replace(
                "_PLUGINS", str(instance.plugins) if instance.plugins else "None"
            )
            self.query_one("#manageinstanceinfo", Markdown).update(game_info)
