---
title: Usage
layout: default
nav_order: 2
parent: Mod Organizer 2 Linux Installer
---

# Using MO2-LINT

> NOTE: Prior to following the instructions on this page, please read through the [Game-Specific Instructions](./game-specific) section of the documentation, as there may be important information or specific steps required for your game.

Below are the commands available in MO2-LINT. All commands accept `--log-level` (`-l`) to control verbosity (`DEBUG`, `INFO`, or `TRACE`), and `--unattended` (`-u`) to skip interactive prompts and use defaults.

## `install`

Creates a new Mod Organizer 2 instance for the specified game.

```bash
mo2-lint install <game> <directory> [options]
```

> #### Parameters
> `<game>` and `<directory>` are required.
>
> - `<game>` - The game identifier (e.g. `skyrim`, `fallout4`). Run `mo2-lint install --help` for the full list of supported games.
> - `<directory>` - The path where the MO2 instance will be created.

> #### Options
> - `--plugin <plugin>`, `-p <plugin>` - Install a plugin into the new MO2 instance. Can be specified multiple times:
>   ```bash
>   mo2-lint install skyrim /path/to/instance -p root-builder -p nxm-collection-dl
>   ```
>   Run `mo2-lint install --help` for the list of available plugins.
>
> - `--script-extender`, `-s` - Install the script extender for the game (e.g. SKSE for Skyrim, F4SE for Fallout 4), if one is available. If multiple versions exist, you will be prompted to choose. Ignored if the game has no script extender.
>   - If you need different script extender versions across instances, omit this flag and configure the script extender via the `root-builder` plugin instead.
>
> - `--launcher <launcher>`, `-L <launcher>` - Force a specific launcher (`steam`, `gog`, or `epic`) instead of auto-detecting.
>
> - `--mo2-archive <path/to/archive>` - Install Mod Organizer 2 from a local `.zip`/`.7z` archive instead of downloading the bundled version. Useful for offline installs or holding an instance at a specific MO2 build. Requires `--mo2-checksum`. The instance is automatically pinned (see [`pin`](#pin)) so a later `update` will not overwrite your chosen build.
>   ```bash
>   mo2-lint install skyrim /path/to/instance --mo2-archive ~/Downloads/Mod.Organizer-2.5.2.7z --mo2-checksum <sha256>
>   ```
>
> - `--mo2-checksum <sha256>` - The expected SHA-256 checksum of the `--mo2-archive` file. Required when `--mo2-archive` is used; the archive is verified against it before extraction.
>
> - `--custom <path/to/file.yml>` - **[Advanced users only, unsupported]** Use a custom game info file. See [Adding Custom Games](./custom-games) for details.

After installation, **launch the game through Steam or Heroic** to confirm the launch option was created. You should see a "Launch Mod Organizer" entry alongside the default launch option.

## `uninstall`

Removes an existing MO2 instance - unregisters the launch option and removes the entry from the state file. Without options, lists all instances and lets you choose one or more to remove.

```bash
mo2-lint uninstall [options]
```

> #### Options
> - `--game <game>`, `-g <game>` - Filter to instances for the specified game.
> - `--directory <directory>`, `-d <directory>` - Filter to instances at or within the specified directory.

> **Note:** `uninstall` does not delete your mod files. Your `mods/`, `profiles/`, and `overwrite/` folders remain on disk.

## `list`

Lists all Mod Organizer 2 instances currently tracked by MO2-LINT.

```bash
mo2-lint list [options]
```

> #### Options
> - `--game <game>`, `-g <game>` - Filter to instances for the specified game.
> - `--directory <directory>`, `-d <directory>` - Filter to instances at or within the specified directory.

## `pin`

Prevents an instance's Mod Organizer 2 version from being changed by `update`. Useful when a newer MO2 version breaks compatibility with specific mods or plugins.

```bash
mo2-lint pin <directory>
```

> #### Parameters
> `<directory>` is required and must be the exact path to the instance - parent directories are not accepted.

## `unpin`

Reverses the effect of `pin`, allowing `update` to change the MO2 version again.

```bash
mo2-lint unpin <directory>
```

> #### Parameters
> `<directory>` is required and must be the exact path to the instance - parent directories are not accepted.

## `update`

Updates the MO2 executable and NXM handler for an existing instance, and refreshes its launch option.

```bash
mo2-lint update <directory> [options]
```

> #### Parameters
> `<directory>` is required and must be the exact path to the instance.

> #### Options
> - `--mo2-archive <path/to/archive>` - Update Mod Organizer 2 from a local `.zip`/`.7z` archive instead of downloading the bundled version. Requires `--mo2-checksum`. After the update the instance is automatically pinned so a later bundled `update` will not overwrite it.
>   ```bash
>   mo2-lint update ~/Games/instance --mo2-archive ~/Downloads/Mod.Organizer-2.5.2.7z --mo2-checksum <sha256>
>   ```
>
> - `--mo2-checksum <sha256>` - The expected SHA-256 checksum of the `--mo2-archive` file. Required when `--mo2-archive` is used; the archive is verified against it before extraction.

> **Note:** If the instance is pinned, the MO2 version will not be updated by a normal `update`. Run `mo2-lint unpin <directory>` first **or** supply `--mo2-archive`, which overrides the pin for that update (and re-pins the instance afterward).

## The Instance State File

MO2-LINT tracks all managed instances in a state file at `~/.config/mo2-lint/state.json`. This file is read and written automatically by the `install`, `uninstall`, `list`, `pin`, `unpin`, and `update` commands.

**Do not edit this file manually.** Doing so may cause inconsistencies or errors when managing instances.
