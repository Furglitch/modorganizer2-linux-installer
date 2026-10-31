from pathlib import Path

from textual.app import Screen, ComposeResult
from textual.containers import VerticalGroup
from textual.widgets import (
    Checkbox,
    Header,
    Footer,
    Input,
    OptionList,
    SelectionList,
)
from util import variables as var


class ManageSettings(Screen):
    SUB_TITLE = "Installer Settings"

    def compose(self) -> ComposeResult:
        yield Header()
        yield self.Settings()
        yield Footer()

    class Settings(VerticalGroup):
        def compose(self) -> ComposeResult:
            # installer.log_level
            _setting = var.settings.log_level or "info"
            _levels = ["info", "debug", "trace"]
            _level_list = [
                f"* {lvl.capitalize()}" if lvl == _setting else lvl.capitalize()
                for lvl in _levels
            ]
            log_level = OptionList(*_level_list)
            log_level.border_title = "Log Level"
            yield log_level

            # installer.check_updates
            yield Checkbox("Check for MO2-LINT updates", var.settings.check_updates)

            # installer.refresh_configs
            yield Checkbox("Refresh configs", var.settings.refresh_configs)

            # instance.launcher
            _setting = var.settings.launcher or "gog"
            _launchers = ["steam", "gog", "epic"]
            _launcher_list = [
                f"* {lnc.capitalize()}" if lnc == _setting else lnc.capitalize()
                for lnc in _launchers
            ]
            launcher = OptionList(*_launcher_list)
            launcher.border_title = "Primary Launcher"
            yield launcher

            # instance.theme
            _setting = var.settings.theme or "none"
            _themes = ["None"] + [theme for theme in var.theme_info]
            _theme_list = [f"* {thm}" if thm == _setting else thm for thm in _themes]
            theme = OptionList(*_theme_list)
            theme.border_title = "Primary MO2 Theme"
            yield theme

            # instance.plugins
            _setting = var.settings.plugins or "none"
            _plugins = ["None"] + [plugin for plugin in var.plugin_info]
            _plugins_list = [
                (plg, idx, plg in _setting) for idx, plg in enumerate(_plugins)
            ]
            plugins = SelectionList(*_plugins_list)
            plugins.border_title = "Primary MO2 Plugins"
            yield plugins

            # instance.folders.root_folder
            _value = str(var.settings.root_folder)
            _placeholder = str(Path("~/Games/mo2-lint").expanduser())
            root_folder = Input(value=_value, placeholder=_placeholder)
            root_folder.border_title = "Default Instance Folder"
            yield root_folder

            # instance.folders.folder_name
            _value = str(var.settings.folder_name)
            _placeholder = "e.g. mo2-{game}-{launcher} | Accepts {game} and {launcher} placeholders."
            folder_name = Input(value=_value, placeholder=_placeholder)
            folder_name.border_title = "Instance Folder Name"
            yield folder_name
