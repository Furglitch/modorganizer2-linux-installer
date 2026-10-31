from textual.app import Screen, ComposeResult
from textual.containers import HorizontalGroup, VerticalGroup
from textual.widgets import (
    Button,
    Checkbox,
    Header,
    Footer,
    Markdown,
    OptionList,
    SelectionList,
)
from util import variables as var

PROGRESS = """
1. Game Select
2. Configure
"""


class InstallGame(Screen):
    TITLE = "MO2-LINT v" + var.version
    SUB_TITLE = "New Instance"

    def compose(self) -> ComposeResult:
        yield Header()
        yield self.InstallScreen()
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
                yield launcher

                games = OptionList(
                    *self.game_list,
                    id="installgamelist",
                )
                games.border_title = "Game"
                yield games

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "installgamenext":
            self.app.push_screen(InstallConfig())


class InstallConfig(Screen):
    TITLE = "MO2-LINT v" + var.version
    SUB_TITLE = "New Instance Settings"

    plugin_list = [(plugin, index) for index, plugin in enumerate(var.plugin_info)]
    theme_list = ["None"] + [theme for theme in var.theme_info]

    def compose(self) -> ComposeResult:
        yield Header()

        yield Checkbox("Script Extender", False, id="installconfigextender")

        plugins = SelectionList(*self.plugin_list, id="installconfigplugins")
        plugins.border_title = "Plugins"
        yield plugins

        plugins = OptionList(*self.theme_list, id="installconfigthemes")
        plugins.border_title = "Themes"
        yield plugins

        yield Button("Next", id="installconfignext")

        yield Footer()

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "installconfignext":
            return  # self.app.push_screen(InstallConfig())
