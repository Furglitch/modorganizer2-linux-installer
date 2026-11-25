from command.pin import pin as _pin
from command.uninstall import uninstall as _uninstall
from command.update import update as _update
from textual.app import Screen, ComposeResult
from textual.containers import HorizontalGroup, VerticalGroup
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    Header,
    Footer,
    Label,
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
    SUB_TITLE = "Manage Instances"
    BINDINGS = [("escape", "app.pop_screen", "Back")]

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
            yield self.ManageChoices(id="manageinstancebuttons")

        class ManageChoices(VerticalGroup):
            def compose(self) -> ComposeResult:
                yield Button("Update", id="manageinstanceupdate")
                yield Button("Pin", id="manageinstancepin")
                yield Button("Uninstall", id="manageinstanceuninstall")
                yield Button("Back", id="manageinstanceback")

    class ConfirmUninstall(ModalScreen[bool]):
        BINDINGS = [("escape", "dismiss(False)", "Cancel")]

        def __init__(
            self,
            message: str = "Are you sure you want to uninstall the selected instance?",
            confirm_label: str = "Uninstall",
        ) -> None:
            super().__init__()
            self.message = message
            self.confirm_label = confirm_label

        def compose(self) -> ComposeResult:
            with VerticalGroup(id="manageuninstallconfirm"):
                yield Label(self.message, id="manageuninstallmessage")
                with HorizontalGroup(id="manageuninstallbuttons"):
                    yield Button(
                        self.confirm_label, id="manageuninstallyes", variant="error"
                    )
                    yield Button("Cancel", id="manageuninstallno")

        def on_button_pressed(self, event: Button.Pressed) -> None:
            event.stop()
            self.dismiss(event.button.id == "manageuninstallyes")

    class TrashChoice(ModalScreen[bool | None]):
        """Dismisses with True for permanent deletion, False for trash, None to cancel."""

        BINDINGS = [("escape", "dismiss(None)", "Cancel")]

        def compose(self) -> ComposeResult:
            with VerticalGroup(id="manageuninstallconfirm"):
                yield Label(
                    "Please choose how to handle the deleted files:",
                    id="manageuninstallmessage",
                )
                with HorizontalGroup(id="manageuninstallbuttons"):
                    yield Button(
                        "Move to Trash", id="manageuninstalltrash", variant="primary"
                    )
                    yield Button(
                        "Delete Permanently",
                        id="manageuninstalldelete",
                        variant="error",
                    )
                    yield Button("Cancel", id="manageuninstallno")

        def on_button_pressed(self, event: Button.Pressed) -> None:
            event.stop()
            if event.button.id == "manageuninstalltrash":
                self.dismiss(False)
            elif event.button.id == "manageuninstalldelete":
                self.dismiss(True)
            else:
                self.dismiss(None)

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
        if event.button.id == "manageinstanceback":
            self.app.pop_screen()
            return

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
            self.app.run_command(
                f"Updating {instance.display_name}", _update, instance.instance_path
            )
        elif event.button.id == "manageinstancepin":
            _pin(instance.instance_path, pin=not instance.pin)
        elif event.button.id == "manageinstanceuninstall":

            def uninstall(permanent: bool) -> None:
                self.app.run_command(
                    f"Uninstalling {instance.display_name}",
                    _uninstall,
                    directory=instance.instance_path,
                    confirmed=True,
                    permanent=permanent,
                    callback=lambda _: self.refresh_instances(index),
                )

            def confirm_permanent(confirmed: bool | None) -> None:
                # Declining permanent deletion falls back to trash, as in the CLI.
                uninstall(bool(confirmed))

            def choose_trash(permanent: bool | None) -> None:
                if permanent is None:
                    return
                if permanent:
                    self.app.push_screen(
                        self.ConfirmUninstall(
                            "Are you sure you want to permanently delete this? This action cannot be undone.",
                            "Delete Permanently",
                        ),
                        confirm_permanent,
                    )
                else:
                    uninstall(False)

            def confirm(confirmed: bool | None) -> None:
                if not confirmed:
                    return
                if instance.instance_path.exists():
                    self.app.push_screen(self.TrashChoice(), choose_trash)
                else:
                    uninstall(False)

            self.app.push_screen(self.ConfirmUninstall(), confirm)
            return
        else:
            return

        self.refresh_instances(index)

    def refresh_instances(self, index: int = 0) -> None:
        instances = self.query_one("#manageinstancelist", OptionList)
        instances.clear_options()
        instances.add_options(
            str(instance.display_name) for instance in state.state_file.instances
        )
        if instances.option_count:
            instances.highlighted = min(index, instances.option_count - 1)
