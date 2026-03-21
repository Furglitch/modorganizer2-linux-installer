---
title: Troubleshooting
layout: default
nav_order: 4
parent: Mod Organizer 2 Linux Installer
---

# Troubleshooting

This page covers common issues and their solutions when using MO2-LINT.

## MO2 Won't Launch

### Check Launch Options

If you are adding anything to your arguments in Steam, ensure you include `%command%`:
```
%command%
```

Variables go before `%command%`, flags go after:
```
VARIABLE=value %command% --flag
```

`%command%` only needs to be added *once*. Adding it multiple times *will* cause problems.


### Flatpak Steam Issues

If you have Steam installed via Flatpak, MO2 may not have access to necessary files. Grant Steam access to your home directory:

```bash
flatpak override --user --filesystem=home com.valvesoftware.Steam
```

If you install the MO2 instance outside of $HOME, change `home` to the appropriate directory. i.e. `--filesystem=/path/to/directory`.

### GameMode Interference

Adding `gamemoderun` to the Steam launch arguments typically improves performance for a Proton game, but it *will* cause MO2 to fail to launch. Remove `gamemoderun` from the launch options if you have it.

### Directories Outside Home

If MO2 or your game is installed outside your home directory, add the path to `STEAM_COMPAT_MOUNTS`:

```bash
STEAM_COMPAT_MOUNTS="/path/to/directory" %command%
```

Multiple directories can be separated with colons:
```bash
STEAM_COMPAT_MOUNTS="/path/to/dir1:/path/to/dir2" %command%
```

## Nexus Mod Links Not Working

### Check Handler Files Exist

Ensure these files exist and are not empty:
- `~/.local/share/mo2-lint/nxm_handler`
- `~/.local/share/applications/mo2lint_nxm_handler.desktop`

If they're missing, try reinstalling MO2-LINT.

### Verify Handler Registration

Check if the handler is registered correctly:
```bash
xdg-mime query default x-scheme-handler/nxm
```

This should return `mo2lint_nxm_handler.desktop`. If not, register it manually:
```bash
xdg-mime default ~/.local/share/applications/mo2lint_nxm_handler.desktop x-scheme-handler/nxm
```

### Check Browser Settings

Some browsers have their own settings for protocol handlers. Ensure your browser is configured to use the system default for `nxm` links.

### qtpaths Error

If you see `/usr/bin/xdg-mime: line 885: qtpaths: command not found` in the logs, create a symlink:
```bash
sudo ln -s /usr/bin/qtpaths6 /usr/bin/qtpaths
```

This issue has been encountered on Fedora 41+ and Manjaro with KDE 6.

## Proton Issues

### Wrong Proton Version

MO2-LINT currently only supports Proton 10.0. Ensure your game is configured to use Proton 10:
- **Steam**: Properties > Compatibility > Force use of specific Steam Play compatibility tool > Proton 10.0
- **Heroic**: Settings > Wine > Wine Version > Proton - Proton 10.0

### Prefix Not Initialized

Launch the game at least once through Steam/Heroic before installing MO2-LINT. This allows the launcher to set up the Proton prefix with default dependencies.

## Instance Issues

### Instance Not Found

If `mo2-lint list` doesn't show your instance, the state file may be out of date. The state file is located at:
```
~/.config/mo2-lint/state.json
```

> **Warning:** Do not manually edit this file. If it becomes corrupted, you may need to reinstall MO2-LINT instances.

### Cannot Update Pinned Instance

Pinned instances will not update their MO2 version. To update a pinned instance, first unpin it:
```bash
mo2-lint unpin /path/to/instance
```

## Log Files

Installation and error logs are stored in:
```
~/.cache/mo2-lint/logs/
```

These logs can be helpful when reporting issues.

## Reporting Issues

If you encounter an issue not covered here:

1. Check the [GitHub Issues](https://github.com/furglitch/modorganizer2-linux-installer/issues) to see if it's already reported
2. If an existing issue is not found, open a new issue with as much detail as possible. Include logs and, if applicable, screenshots.
