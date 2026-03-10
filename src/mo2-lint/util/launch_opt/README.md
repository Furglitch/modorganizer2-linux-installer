# launch-opt

Contains the functions for parsing and editing the launch options of a game from appinfo.vdf.

This is used to add the MO2 instance link to the launch options of the desired game.

## Usage

The `editor.py` file can be used as a standalone script to read and edit the appinfo.vdf file.

```bash
PYTHONPATH=src/mo2-lint python3 src/mo2-lint/util/launch_opt/editor.py read [AppID]
```

```bash
PYTHONPATH=src/mo2-lint python3 src/mo2-lint/util/launch_opt/editor.py add [AppID] [/path/to/executable] [OPTIONS]
```

```bash
PYTHONPATH=src/mo2-lint python3 src/mo2-lint/util/launch_opt/editor.py remove [AppID] [Option #]
```

## Attribution

`appinfo.py` is sourced from [tralph3/Steam-Metadata-Editor](https://github.com/tralph3/Steam-Metadata-Editor) and is distributed under the GNU General Public License v3.0.
