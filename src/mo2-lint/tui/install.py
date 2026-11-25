from pathlib import Path

from command.install import get_install_dir, install as _install
from textual.app import Screen, ComposeResult
from textual.containers import HorizontalGroup, VerticalGroup
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    Checkbox,
    Header,
    Footer,
    Input,
    Label,
    Markdown,
    OptionList,
    SelectionList,
)
from util import state_file as state
from util.lang import prefix_instructions
from util import variables as var

LAUNCHERS = ("steam", "gog", "epic")  # Same order as GameSelect.launcher_list

PROGRESS = """
1. Game Select
2. Configure
"""


class InstallGame(Screen):
    TITLE = "MO2-LINT v" + var.version
    SUB_TITLE = "New Instance"
    BINDINGS = [("escape", "app.pop_screen", "Back")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield self.InstallScreen()
        with HorizontalGroup(id="installgamenav"):
            yield Button("Back", id="installgameback")
            yield Button("Next", id="installgamenext")
        yield Footer()

    class InstallScreen(HorizontalGroup):
        def compose(self) -> ComposeResult:
            yield self.GameSelect()
            yield Markdown(PROGRESS, id="installprogress")

        class GameSelect(VerticalGroup):
            launcher_list = ["Steam", "GOG", "Epic Games"]
            game_list = [info.display_name for info in var.games_info.values()]

            def compose(self) -> ComposeResult:
                launcher = OptionList(
                    *self.launcher_list,
                    id="installgamelauncher",
                )
                launcher.border_title = "Launcher"
                if var.settings.launcher in LAUNCHERS:
                    launcher.highlighted = LAUNCHERS.index(var.settings.launcher)
                yield launcher

                games = OptionList(
                    *self.game_list,
                    id="installgamelist",
                )
                games.border_title = "Game"
                yield games

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "installgameback":
            self.app.pop_screen()
        elif event.button.id == "installgamenext":
            launcher = self.query_one("#installgamelauncher", OptionList).highlighted
            game = self.query_one("#installgamelist", OptionList).highlighted
            if game is None:
                self.notify("Select a game to continue.", severity="warning")
                return
            self.app.push_screen(
                InstallConfig(
                    list(var.games_info)[game],
                    LAUNCHERS[launcher] if launcher is not None else None,
                )
            )


class InstallConfig(Screen):
    TITLE = "MO2-LINT v" + var.version
    SUB_TITLE = "New Instance Settings"
    BINDINGS = [("escape", "app.pop_screen", "Back")]

    plugin_list = [
        (plugin, plugin, plugin in var.settings.plugins) for plugin in var.plugin_info
    ]
    theme_list = ["None"] + [theme for theme in var.theme_info]

    def __init__(self, game: str, launcher: str | None) -> None:
        super().__init__()
        self.game = game
        self.launcher = launcher

    def compose(self) -> ComposeResult:
        yield Header()

        yield Checkbox("Script Extender", False, id="installconfigextender")

        plugins = SelectionList(*self.plugin_list, id="installconfigplugins")
        plugins.border_title = "Plugins"
        yield plugins

        plugins = OptionList(*self.theme_list, id="installconfigthemes")
        plugins.border_title = "Themes"
        plugins.highlighted = (
            self.theme_list.index(var.settings.theme)
            if var.settings.theme in self.theme_list
            else 0
        )
        yield plugins

        if var.settings.root_folder:
            try:
                # "{launcher}" is shown as-is when the launcher is auto-detected.
                default = get_install_dir(
                    self.game,
                    None,
                    self.launcher or var.settings.launcher or "{launcher}",
                )
            except SystemExit:
                default = var.settings.root_folder
            placeholder = f"Default: {default}"
        else:
            placeholder = "Required: no default instance folder is set in Settings."
        directory = Input(placeholder=placeholder, id="installconfigdirectory")
        directory.border_title = "Install Directory"
        yield directory

        with HorizontalGroup(id="installconfignav"):
            yield Button("Back", id="installconfigback")
            yield Button("Next", id="installconfignext")

        yield Footer()

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "installconfigback":
            self.app.pop_screen()
        elif event.button.id == "installconfignext":
            directory = self.query_one("#installconfigdirectory", Input).value.strip()
            if not directory and not var.settings.root_folder:
                self.notify(
                    "Enter an install directory, or set a default instance folder in Settings.",
                    severity="error",
                )
                return
            directory = (
                Path(directory.rstrip("/")).expanduser().resolve()
                if directory
                else None
            )

            theme = self.query_one("#installconfigthemes", OptionList).highlighted
            theme = self.theme_list[theme] if theme else None
            plugins = tuple(
                self.query_one("#installconfigplugins", SelectionList).selected
            )
            script_extender = self.query_one("#installconfigextender", Checkbox).value

            def run_install(prefix_confirmed: bool | None) -> None:
                def install() -> None:
                    var.load_game_info(self.game)
                    _install(
                        self.game,
                        directory,
                        log_level=var.settings.log_level or "INFO",
                        script_extender=script_extender,
                        plugin=plugins,
                        theme=theme,
                        launcher=self.launcher,
                        prefix_confirmed=prefix_confirmed,
                    )
                    state.write_state()

                def on_complete(completed: bool | None) -> None:
                    if completed:
                        # Back to the main menu.
                        self.app.pop_screen()
                        self.app.pop_screen()

                self.app.run_command(
                    f"Installing {var.games_info[self.game].display_name}",
                    install,
                    callback=on_complete,
                )

            def on_prefix_setup(choice: str | None) -> None:
                if choice == "installprefixyes":
                    run_install(True)
                elif choice == "installprefixno":
                    run_install(False)

            if self.launcher:
                self.app.push_screen(
                    self.PrefixSetup(prefix_instructions(self.launcher, self.game)),
                    on_prefix_setup,
                )
            else:
                # No launcher picked; the installer detects it and prompts as usual.
                run_install(None)

    class PrefixSetup(ModalScreen[str | None]):
        BINDINGS = [("escape", "dismiss(None)", "Cancel")]

        def __init__(self, instructions: str) -> None:
            super().__init__()
            self.instructions = instructions

        def compose(self) -> ComposeResult:
            with VerticalGroup(id="installprefixdialog"):
                yield Label(self.instructions, id="installprefixmessage", markup=False)
                yield Label("Have you completed these steps?")
                with HorizontalGroup(id="installprefixbuttons"):
                    yield Button("Yes", id="installprefixyes", variant="success")
                    yield Button("No, continue anyway", id="installprefixno")
                    yield Button("Cancel", id="installprefixcancel")

        def on_button_pressed(self, event: Button.Pressed) -> None:
            event.stop()
            self.dismiss(
                None if event.button.id == "installprefixcancel" else event.button.id
            )
