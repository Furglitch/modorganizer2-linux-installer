---
title: Post-Installation Steps
layout: default
nav_order: 1
parent: Installation
---

# Post-Installation Steps

After successfully installing Mod Organizer 2 Linux Installer, there are a few additional steps you may want to take to ensure everything is set up correctly.

## First Run
When you run the application for the first time, it will take you through the MO2 setup process.

A few steps need special attention:
- **"Select the type of instance to create"**: It's recommended to select "Portable" so that all files are stored in the MO2 instance directory, making it easier to manage and backup your mods and profiles.
- **"Select the game to manage."**: Other games may appear in the list. Choose the game you selected during installation.
  - Additionally, your game may not be detected. If this is the case, you can select "Browse" and navigate to your game's installation directory to select it.
- **"Configure your profile settings."**: Up to personal preference. Use profile specific saves and INIs as you normall would.
  - Note: Profile-specific saves and INIs will be stored in the `profiles` directory within your MO2 installation directory, not in your game's directory like normal savegames.
- **"Select a folder where the data should be stored."**: Should be set to the MO2 instance directory by default. Do not change this, unless it is not set to the MO2 instance directory.
- **Link Mod Organizer with your Nexus account**: Optional, but recommended if you want to use the '*Mod manager download*' feature on Nexus Mods.

After confirming your setup, before installing any mods, it's recommended to run the game once to ensure that it is working correctly with MO2. This will allow you to verify that the game is launching properly and that MO2 is configured correctly before you start installing mods.

## Flatpak Users
If you have Steam installed via Flatpak, you may encounter issues with MO2 not loading as expected. This is because Flatpak applications are sandboxed and may not have access to the necessary files and directories.

```bash
flatpak override --user --filesystem=home com.valvesoftware.Steam
```
The above command will grant the Steam Flatpak access to your home directory, which should allow MO2 to launch correctly.

This fix should be applied when MO2-LINT runs, but if you encounter issues with MO2 not launching, please try running the above command and then restarting MO2-LINT.

## Launch Options

#### First, a note
Remember, when adding anything to Launch Options, you must include the `%command%` argument, otherwise MO2 will not launch.
Variables go before `%command%`, and flags go after. For example:
```
BEFORE=true %command% --after
```

### Directories outside of Home
When trying to install MO2 in a directory outside of your home directory, or access files outside of your home directory, you may encounter issues with MO2 not launching or not being able to access the necessary files.

This can be resolved with the `STEAM_COMPAT_MOUNTS` variable in your Launch Options. This variable allows you to specify additional directories that Steam should mount for the game.
```
STEAM_COMPAT_MOUNTS="/path/to/directory1":"/path/to/directory2" %command%
```
In the above example, replace `/path/to/directory1` and `/path/to/directory2` with the actual paths to the directories you want to access. You can add as many directories as needed, just make sure to separate them with a colon (`:`).

### Launching without opening MO2
The `moshortcut://` protocol allows you to launch a MO2 profile directly without opening the MO2 interface. This can be useful if you want to quickly launch the game with a specific profile without having go into MO2.
This is especially useful for users who have finished setting up their MO2 instance and just want to launch the modded game directly from Steam.

```
%command% 'moshortcut://"SKSE"'
```
The above example will launch the main profile's SKSE shortcut, without needing to navigate through the MO2 interface. You can replace `SKSE` with the name of any shortcut in your MO2 instance to launch that specific shortcut directly.

### `gamemoderun`
Usually, `gamemoderun` can provide a performance boost for games on Linux by optimizing system resources. However, it can sometimes cause issues with MO2, such as preventing it from launching or causing it to crash. If you encounter issues with MO2 not launching or crashing, try removing `gamemoderun` from your Launch Options to see if that resolves the issue.

## Nexus Links
If you notice that Nexus links are not working in MO2, it's possible that the handler did not install or register correctly. To fix this, you can try the following steps:

1. Ensure that `~/.local/share/mo2-lint/nxm_handler` and `~/.local/share/applications/mo2lint_nxm_handler.desktop` exist and are not empty/corrupted.
   - If they do not exist, try reinstalling MO2-LINT to see if that resolves the issue.
2. Check that the handler is registered correctly by running the following command in your terminal:
   ```bash
   xdg-mime query default x-scheme-handler/nxm
   ```
   This should return `mo2lint_nxm_handler.desktop`. If it does not, you can manually set it with the following command:
   ```bash
   xdg-mime default ~/.local/share/applications/mo2lint_nxm_handler.desktop x-scheme-handler/nxm
   ```
3. It's also possible that your browser is not set to use the system's default handler for `nxm` links. Check your browser's settings to ensure that it is configured to use the system's default handler for `nxm` links.
4. Check the install logs (located in `~/.cache/mo2-lint/logs`) for the error message `/usr/bin/xdg-mime: line 885: qtpaths: command not found`. Fixing this error is simple, just creating a symlink to `qtpaths` should resolve the issue:
   ```bash
   sudo ln -s /usr/bin/qtpaths6 /usr/bin/qtpaths
   ```
   - Issue 4 has been encountered on Fedora 41+ and Manjaro, and potentially affects other distros using KDE 6 as well. Solution was found by [sf:witt](https://segmentfault.com/a/1190000045432085)

## Alternative Proton Versions
As of version 7.0.0, MO2-LINT only supports installs using Proton 10.0. The developer provides no guarantee that alternative versions will be stable or work at all with MO2-LINT, and will not provide support for any issues encountered while using alternative versions.

(Previous versions supported Proton 9, but this was updated to Proton 10 as a Fallout 4 update broke compatibility with Proton 9.)
