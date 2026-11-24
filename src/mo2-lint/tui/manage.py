from command.pin import pin as _pin
from command.uninstall import uninstall as _uninstall
from command.update import update as _update
from textual.app import Screen, ComposeResult
from textual.containers import HorizontalGroup, VerticalGroup
from textual.widgets import (
    Button,
    Header,
    Footer,
    Markdown,
    OptionList,
)
from util import state_file as state

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

        def compose(self) -> ComposeResult:
            instances = OptionList(*self.instance_list, id="manageinstancelist")
            instances.border_title = "Instances"
            yield instances
            yield Markdown(INSTANCE_INFO, id="manageinstanceinfo")
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
            self.query_one("#manageinstancepin", Button).label = (
                "Unpin" if instance.pin else "Pin"
            )

    def on_mount(self) -> None:
        self.refresh_instances()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        index = self.query_one("#manageinstancelist", OptionList).highlighted
        if index is None:
            return
        instance = state.state_file.instances[index]

        if event.button.id == "manageinstanceupdate":
            if instance.pin:
                self.notify(
                    "Instance is pinned. Unpin it to update.", severity="warning"
                )
                return
            self.run_command(_update, instance.instance_path)
        elif event.button.id == "manageinstancepin":
            _pin(instance.instance_path, pin=not instance.pin)
        elif event.button.id == "manageinstanceuninstall":
            self.run_command(_uninstall, directory=instance.instance_path)
        else:
            return

        self.refresh_instances(index)

    def run_command(self, command, *args, **kwargs) -> None:
        """Runs a CLI command with the TUI suspended, so its prompts and output work as normal."""
        with self.app.suspend():
            try:
                command(*args, **kwargs)
            except (SystemExit, KeyboardInterrupt):
                print("\nCommand did not complete.")
            input("\nPress Enter to return to MO2-LINT...")

    def refresh_instances(self, index: int = 0) -> None:
        instances = self.query_one("#manageinstancelist", OptionList)
        instances.clear_options()
        instances.add_options(
            str(instance.display_name) for instance in state.state_file.instances
        )
        if instances.option_count:
            instances.highlighted = min(index, instances.option_count - 1)
