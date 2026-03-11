# launch-opt

Contains functions for parsing and editing launch options across different game launchers.

This is used to add the MO2 instance link to the launch options of the desired game.

## Structure

- **editor.py** - High-level wrapper/dispatcher providing a unified interface
- **steam.py** - Steam-specific implementation (appinfo.vdf parsing)
- **epic.py** - Epic Games (Heroic) implementation (JSON-based)
- **gog.py** - GOG Games (Heroic) implementation (JSON-based)
- **appinfo.py** - VDF parser library for Steam

## Usage

### Programmatic API

Use the unified interface from `editor.py`:

```python
from util.launch_opt.editor import add_launch_option, remove_launch_option, read_launch_option

# Add a launch option
add_launch_option(
    launcher="steam",  # or "epic"
    game_id=1091500,   # appid for Steam, epic_id string for Epic
    executable="mo2-redirector.exe",
    label="Launch Mod Organizer"
)

# GOG example (requires game_path)
add_launch_option(
    launcher="gog",
    game_id="1458058109",
    game_path="/path/to/game/install",
    executable="mo2-redirector.exe",
    label="Launch Mod Organizer"
)

# Remove a launch option
remove_launch_option(
    launcher="steam",
    game_id=1091500,
    index=5  # For Steam (required)
)

remove_launch_option(
    launcher="epic",
    game_id="77f2b98e2cef40c8a7437518bf420e47",
    label="Launch Mod Organizer"  # For Epic (matches by name)
)

remove_launch_option(
    launcher="gog",
    game_id="1458058109",
    game_path="/path/to/game/install",
    label="Launch Mod Organizer"  # For GOG (matches by name)
)
```

### Command Line

The `editor.py` file can be used as a standalone script for both Steam and Epic:

**Reading launch options:**
```bash
# Steam
PYTHONPATH=src:src/mo2-lint python3 -m util.launch_opt.editor read -l steam <AppID>

# Epic
PYTHONPATH=src:src/mo2-lint python3 -m util.launch_opt.editor read -l epic <EpicGameID>

# GOG
PYTHONPATH=src:src/mo2-lint python3 -m util.launch_opt.editor read -l gog <GOGGameID> --game-path /path/to/game/install
```

**Adding a launch option:**
```bash
# Steam
PYTHONPATH=src:src/mo2-lint python3 -m util.launch_opt.editor add -l steam <AppID> <executable> --label "My Option" [OPTIONS]

# Epic
PYTHONPATH=src:src/mo2-lint python3 -m util.launch_opt.editor add -l epic <EpicGameID> <executable> --label "My Option"

# GOG
PYTHONPATH=src:src/mo2-lint python3 -m util.launch_opt.editor add -l gog <GOGGameID> <executable> --label "My Option" --game-path /path/to/game/install
```

**Removing a launch option:**
```bash
# Steam (requires index)
PYTHONPATH=src:src/mo2-lint python3 -m util.launch_opt.editor remove -l steam <AppID> --index <Index>

# Epic (requires label)
PYTHONPATH=src:src/mo2-lint python3 -m util.launch_opt.editor remove -l epic <EpicGameID> --label "My Option"

# GOG (requires label and game path)
PYTHONPATH=src:src/mo2-lint python3 -m util.launch_opt.editor remove -l gog <GOGGameID> --label "My Option" --game-path /path/to/game/install
```

For more options, use `--help` on any command.

## Attribution

`appinfo.py` is sourced from [tralph3/Steam-Metadata-Editor](https://github.com/tralph3/Steam-Metadata-Editor) and is distributed under the GNU General Public License v3.0.
