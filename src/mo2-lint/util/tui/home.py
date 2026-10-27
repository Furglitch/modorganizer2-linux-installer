from textual.app import App, ComposeResult, RenderResult
from textual.widgets import Header, Footer, OptionList, Label
from .. import variables as var
from .. import lang
from ..state_file import instance_count


class Dashboard(App):
    TITLE = "MO2-LINT v" + var.version
    SUB_TITLE = ""
    CSS_PATH = "tui.tcss"
    BINDINGS = [("t", "toggle_dark", "Toggle Theme")]

    MENU_ITEMS = [
        "Create New Instance",
        "Manage Instances",
        "Settings",
        "Documentation",
        "Exit",
    ]

    def on_mount(self) -> None:
        self.theme = "catppuccin-mocha"

    def compose(self) -> ComposeResult:
        yield Header()
        yield self.Logo(id="dashhead")
        yield OptionList(
            *[f"{item}" for item in self.MENU_ITEMS], id="dashmenu", markup=False
        )
        yield self.Count(id="dashcount")
        yield Footer()

    def on_option_list_option_highlighted(
        self, event: OptionList.OptionHighlighted
    ) -> None:
        if event.option_list.id == "dashmenu":
            option_list = event.option_list
            new_options = [
                f"[> {item} <]" if idx == event.option_index else f"[{item}]"
                for idx, item in enumerate(self.MENU_ITEMS)
            ]

            options = [
                str(option_list.get_option_at_index(i).prompt)
                for i in range(option_list.option_count)
            ]
            if options != new_options:
                option_list.clear_options()
                option_list.add_options(new_options)
                option_list.highlighted = event.option_index

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        if event.option_list.id != "dashmenu":
            return

        if event.option_index == 0:  # Create New Instance
            from .install import InstallGame

            self.push_screen(InstallGame())
        if event.option_index == 1:  # Manage Instances
            from .manage import ManageInstance

            self.push_screen(ManageInstance())
        if event.option_index == 2:  # Settings
            from .settings import ManageSettings

            self.push_screen(ManageSettings())
        if event.option_index == 3:  # Documentation
            from webbrowser import open

            open("https://docs.furglitch.com/modorganizer2-linux-installer/")
        elif event.option_index == 4:  # Exit
            self.exit()

    def action_toggle_dark(self) -> None:
        self.theme = (
            "catppuccin-mocha"
            if self.theme == "catppuccin-latte"
            else "catppuccin-latte"
        )

    class Logo(Label):
        def render(self) -> RenderResult:
            return lang.ASCII

    class Count(Label):
        def render(self) -> RenderResult:
            return f"[Total Instances: {instance_count()}]"
