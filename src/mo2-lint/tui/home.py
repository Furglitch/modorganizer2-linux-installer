from threading import Event

from loguru import logger
from shared.logger import add_loggers, remove_loggers
from textual import events
from textual.app import App, ComposeResult, RenderResult
from textual.containers import HorizontalGroup, VerticalGroup
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    Header,
    Footer,
    OptionList,
    Label,
    ProgressBar,
    RichLog,
)
from util import variables as var
from util import lang
from util.state_file import instance_count


MIN_WIDTH = 120
MIN_HEIGHT = 30


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

    progress = None  # The open CommandProgress screen, if any

    def on_mount(self) -> None:
        self.theme = "catppuccin-mocha"
        self.add_loggers()
        lang.tui_choice = self.ask_choice
        self.update_menu()
        self.check_size()
        self.screen_change_signal.subscribe(self, self.update_menu)

    def add_loggers(self) -> None:
        """
        Sends console logging to the TUI instead of stdout, at the log level from settings.
        """
        remove_loggers()
        add_loggers(
            log_level=var.settings.log_level,
            process="installer",
            console_sink=self.log_sink,
        )

    def log_sink(self, message) -> None:
        if self.progress:
            self.progress.write(message)
        elif message.record["level"].no >= logger.level("WARNING").no:
            severity = (
                "error"
                if message.record["level"].no >= logger.level("ERROR").no
                else "warning"
            )
            self.notify(message.record["message"], severity=severity)

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
                self.update_menu()

    def on_resize(self, event: events.Resize) -> None:
        self.check_size(event.size)

    def check_size(self, size=None) -> None:
        """
        Covers the TUI with a notice while the terminal is smaller than the minimum size.
        """
        size = size or self.size
        small = size.width < MIN_WIDTH or size.height < MIN_HEIGHT
        if small and not isinstance(self.screen, self.TooSmall):
            self.push_screen(self.TooSmall())
        elif not small and isinstance(self.screen, self.TooSmall):
            self.pop_screen()

    def update_menu(self, _=None) -> None:
        """
        Disables Manage Instances when there are no instances.
        """
        menu = self.screen_stack[0].query_one("#dashmenu", OptionList)
        disabled = not instance_count()

        if menu.get_option_at_index(1).disabled != disabled:
            if disabled:
                menu.disable_option_at_index(1)
            else:
                menu.enable_option_at_index(1)

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
            self.open_url("https://docs.furglitch.com/modorganizer2-linux-installer/")
        elif event.option_index == 4:  # Exit
            self.exit()

    def ask_choice(self, message: str, choices: list[str]) -> int:
        """
        Shows a list prompt as a modal, for commands running in a separate thread.

        Returns the chosen index, or -1 if cancelled.
        """
        result = []
        answered = Event()

        def on_choice(index: int | None) -> None:
            result.append(-1 if index is None else index)
            answered.set()

        self.call_from_thread(
            self.push_screen, self.Choice(message, choices), on_choice
        )
        answered.wait()
        return result[0]

    def run_command(self, title: str, command, *args, callback=None, **kwargs) -> None:
        """
        Runs a CLI command in a separate thread, showing its progress and log output.

        callback is called with True if the command completed, once the progress screen is closed.
        """
        self.push_screen(self.CommandProgress(title, command, args, kwargs), callback)

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
        def on_mount(self) -> None:
            self.app.screen_change_signal.subscribe(
                self, lambda _: self.refresh()
            )  # Recount on return from other screen

        def render(self) -> RenderResult:
            return f"[Total Instances: {instance_count()}]"

    class CommandProgress(ModalScreen[bool]):
        def __init__(self, title: str, command, args, kwargs) -> None:
            super().__init__()
            self.heading = title
            self.command = command
            self.args = args
            self.kwargs = kwargs
            self.completed = False

        def compose(self) -> ComposeResult:
            with VerticalGroup(id="commanddialog"):
                yield Label(self.heading, id="commandtitle")
                yield Label("Starting...", id="commandstatus", markup=False)
                yield ProgressBar(
                    total=None,
                    show_eta=False,
                    show_percentage=False,
                    id="commandprogress",
                )
                yield RichLog(id="commandlog", wrap=True)
                with HorizontalGroup(id="commandbuttons"):
                    yield Button("Close", id="commandclose", disabled=True)

        def on_mount(self) -> None:
            self.app.progress = self
            # Commands print some messages (e.g. post-install steps) instead of logging them.
            self.app.begin_capture_print(self)
            self.run_worker(self.run_command, thread=True)

        def run_command(self) -> None:
            completed = False
            try:
                self.command(*self.args, **self.kwargs)
                completed = True
            except SystemExit:
                pass
            except Exception:
                logger.exception("Command failed with an unexpected error")
            self.app.call_from_thread(self.finish, completed)

        def finish(self, completed: bool) -> None:
            self.completed = completed
            self.app.end_capture_print(self)
            self.app.progress = None
            self.query_one("#commandprogress", ProgressBar).update(total=1, progress=1)
            self.query_one("#commandstatus", Label).update(
                "Completed." if completed else "Did not complete. See the log above."
            )
            close = self.query_one("#commandclose", Button)
            close.disabled = False
            close.variant = "success" if completed else "error"
            close.focus()

        def write(self, message) -> None:
            """Log sink; called from the command's thread."""
            try:
                self.app.call_from_thread(
                    self.add_line, message.rstrip("\n"), message.record
                )
            except RuntimeError:  # Logged from the app's own thread
                self.add_line(message.rstrip("\n"), message.record)

        def add_line(self, line: str, record=None) -> None:
            self.query_one("#commandlog", RichLog).write(line)
            if record and record["level"].no >= logger.level("INFO").no:
                self.query_one("#commandstatus", Label).update(record["message"])

        def on_print(self, event: events.Print) -> None:
            if event.text.strip():
                self.add_line(event.text.rstrip("\n"))

        def on_button_pressed(self, event: Button.Pressed) -> None:
            event.stop()
            if event.button.id == "commandclose":
                self.dismiss(self.completed)

    class Choice(ModalScreen[int | None]):
        BINDINGS = [("escape", "dismiss(None)", "Cancel")]

        def __init__(self, message: str, choices: list[str]) -> None:
            super().__init__()
            self.message = "\n".join(line.strip() for line in message.splitlines())
            self.choices = choices

        def compose(self) -> ComposeResult:
            with VerticalGroup(id="choicedialog"):
                yield Label(self.message, id="choicemessage", markup=False)
                yield OptionList(*self.choices, id="choicelist", markup=False)
                with HorizontalGroup(id="choicebuttons"):
                    yield Button("Select", id="choiceselect", variant="primary")
                    yield Button("Cancel", id="choicecancel")

        def on_mount(self) -> None:
            self.query_one("#choicelist", OptionList).highlighted = 0

        def on_option_list_option_selected(
            self, event: OptionList.OptionSelected
        ) -> None:
            event.stop()
            self.dismiss(event.option_index)

        def on_button_pressed(self, event: Button.Pressed) -> None:
            event.stop()
            if event.button.id == "choiceselect":
                self.dismiss(self.query_one("#choicelist", OptionList).highlighted)
            else:
                self.dismiss(None)

    class TooSmall(ModalScreen):
        def compose(self) -> ComposeResult:
            yield Label(id="toosmallmessage")

        def on_mount(self) -> None:
            self.show_size()

        def on_resize(self, event: events.Resize) -> None:
            self.show_size()

        def show_size(self) -> None:
            self.query_one("#toosmallmessage", Label).update(
                f"Please resize your terminal to at least {MIN_WIDTH} x {MIN_HEIGHT}.\n"
                f"Current size: {self.app.size.width} x {self.app.size.height}"
            )
