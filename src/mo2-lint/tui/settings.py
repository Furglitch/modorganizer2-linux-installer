from pathlib import Path

from textual.app import ComposeResult, Screen
from textual.containers import VerticalGroup
from textual.widgets import (
    Button,
    Checkbox,
    Footer,
    Header,
    Input,
    OptionList,
    SelectionList,
)
from util import variables as var

LOG_LEVELS = ("info", "debug", "trace")
LAUNCHERS = ("steam", "gog", "epic")


class ManageSettings(Screen):
    SUB_TITLE = "Installer Settings"
    BINDINGS = (("ctrl+s", "save_settings", "Save Settings"),)

    def compose(self) -> ComposeResult:
        yield Header()
        yield self.Settings()
        yield Button("Back", id="settings-back")
        yield Button("Save Settings", id="settings-save")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "settings-save":
            self.action_save_settings()
        elif event.button.id == "settings-back":
            self.app.pop_screen()
        else:
            return

    def action_save_settings(self) -> None:
        log_level = self.query_one("#settings-log-level", OptionList).highlighted
        launcher = self.query_one("#settings-launcher", OptionList).highlighted
        theme = self.query_one("#settings-theme", OptionList).highlighted
        if log_level is None or launcher is None or theme is None:
            return

        themes = ["None", *var.theme_info]
        var.settings.log_level = LOG_LEVELS[log_level]
        var.settings.check_updates = self.query_one(
            "#settings-check-updates", Checkbox
        ).value
        var.settings.refresh_configs = self.query_one(
            "#settings-refresh-configs", Checkbox
        ).value
        var.settings.launcher = LAUNCHERS[launcher]
        var.settings.theme = None if theme == 0 else themes[theme]
        var.settings.plugins = tuple(
            self.query_one("#settings-plugins", SelectionList).selected
        )

        root_folder = self.query_one("#settings-root-folder", Input).value.strip()
        var.settings.root_folder = (
            Path(root_folder).expanduser() if root_folder else None
        )
        folder_name = self.query_one("#settings-folder-name", Input).value.strip()
        var.settings.folder_name = folder_name or None

        var.save_settings()
        self.notify("Settings saved")

    class Settings(VerticalGroup):
        def compose(self) -> ComposeResult:
            # installer.log_level
            _setting = (var.settings.log_level or "info").lower()
            log_level = OptionList(
                *(level.capitalize() for level in LOG_LEVELS), id="settings-log-level"
            )
            log_level.border_title = "Log Level"
            log_level.highlighted = (
                LOG_LEVELS.index(_setting) if _setting in LOG_LEVELS else 0
            )
            yield log_level

            # installer.check_updates
            yield Checkbox(
                "Check for MO2-LINT updates",
                var.settings.check_updates,
                id="settings-check-updates",
            )

            # installer.refresh_configs
            yield Checkbox(
                "Refresh configs",
                var.settings.refresh_configs,
                id="settings-refresh-configs",
            )

            # instance.launcher
            _setting = (var.settings.launcher or "gog").lower()
            launcher = OptionList(
                *(item.capitalize() for item in LAUNCHERS), id="settings-launcher"
            )
            launcher.border_title = "Primary Launcher"
            launcher.highlighted = (
                LAUNCHERS.index(_setting) if _setting in LAUNCHERS else 1
            )
            yield launcher

            # instance.theme
            _themes = ["None", *var.theme_info]
            _setting = var.settings.theme or "None"
            theme = OptionList(*_themes, id="settings-theme")
            theme.border_title = "Primary MO2 Theme"
            theme.highlighted = _themes.index(_setting) if _setting in _themes else 0
            yield theme

            # instance.plugins
            _plugins_list = [
                (plugin, plugin, plugin in var.settings.plugins)
                for plugin in var.plugin_info
            ]
            plugins = SelectionList(*_plugins_list, id="settings-plugins")
            plugins.border_title = "Primary MO2 Plugins"
            yield plugins

            # instance.folders.root_folder
            _value = str(var.settings.root_folder) if var.settings.root_folder else ""
            _placeholder = str(Path("~/Games/mo2-lint").expanduser())
            root_folder = Input(value=_value, placeholder=_placeholder)
            root_folder.border_title = "Default Instance Folder"
            root_folder.id = "settings-root-folder"
            yield root_folder

            # instance.folders.folder_name
            _value = var.settings.folder_name or ""
            _placeholder = "e.g. mo2-{game}-{launcher} | Accepts {game} and {launcher} placeholders."
            folder_name = Input(value=_value, placeholder=_placeholder)
            folder_name.border_title = "Instance Folder Name"
            folder_name.id = "settings-folder-name"
            yield folder_name
