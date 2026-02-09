---
title: Usage
layout: default
nav_order: 2
parent: Installation and Usage
---

# Using MO2-LINT

Below are some of the key commands and features available in MO2-LINT.

## `install`
The `install` command allows you to create a new Mod Organizer 2 instance. You can specify the game and directory for the installation.

```bash
mo2_lint install <game> <directory> [options]
```

> #### Parameters
> `<game>` and `<directory>` are required parameters.<br>
> Where `<game>` is the game you want to install MO2 for (e.g., `skyrim`, `fallout4`), and `<directory>` is the path where you want the MO2 instance to be created.<br>
> Supported games can be seen by running:
> ```bash
> mo2_lint install --help
> ```

> #### Options
> - `--plugin <plugin>`, `-p <plugin>` - Installs the specified plugin into the MO2 instance being created.
>   - This option can be used multiple times to install multiple plugins at once. For example:
>      ```bash
>      mo2_lint install skyrim /path/to/instance -p root-builder -p nxm-collection-dl
>   - Supported plugins can be seen by running:
>     ```bash
>     mo2_lint install --help
>     ```
>
> - `--script-extender`, `-s` - If the game supports a script extender (e.g., SKSE for Skyrim, F4SE for Fallout 4), this option will install the script extender into the game's install directory. If multiple versions are available, you will be prompted to choose which one to install. If the game doesn't support a script extender, this option will be ignored.
>   - If you need to install multiple versions of the script extender, it's recommend to NOT use this option, and instead set up the script extender using the `root-builder` plugin per instance.
>
> - `--custom <path/to/file.yml>` - [ADVANCED USERS ONLY, NOT SUPPORTED] - This allows you to specify a custom gameinfo file to use for the installation. More information on the gameinfo file can be found in the [Custom Games](/custom-games) section of the documentation.

## `uninstall`
The `uninstall` command removes an existing Mod Organizer 2 instance, uninstalling the instance and redirector, and removing it from the state file. Without options, it will list all instances and allow you to choose one (or all) to uninstall.

```bash
mo2_lint uninstall [options]
```

> #### Options
> - `--game <game>`, `-g <game>` - Scans for MO2 instances associated with the specified game and allows you to choose which one(s) to uninstall.
> - `--directory <directory>`, `-d <directory>` - Scans for MO2 instances located at the specified directory and allows you to choose which one(s) to uninstall. You can also specify a parent directory to scan for instances within it's subdirectories.


## `list`
The `list` command displays all Mod Organizer 2 instances currently managed by MO2-LINT.

```bash
mo2_lint list [options]
```

> #### Options
> - `--game <game>`, `-g <game>` - Scans for MO2 instances associated with the specified game and lists them.
> - `--directory <directory>`, `-d <directory>` - Scans for MO2 instances located at the specified directory and lists them. You can also specify a parent directory to scan for instances within it's subdirectories.

## `pin` and `unpin`
The `pin` command allows you to prevent an MO2 instance from having it's Mod Organizer 2 version updated. This is useful if you want to maintain a specific version for compatibility reasons.
To reverse this, you can use the `unpin` command. The same parameters apply, just switching the command name.

```bash
mo2_lint pin <directory> [options]
```

> #### Parameters
> `<directory>` is a required parameter.<br>
> Where `<directory>` is the path of the MO2 instance you want to pin/unpin. You must provide the exact path to the instance you wish to adjust. Higher level directories will not work for this command.

## `update`
The `update` command updates the Mod Organizer 2 install and Redirector of an existing instance, as well as the NXM handler to the latest version.<br>
<sub>If the instance is pinned, the Mod Organizer 2 version will not be updated.</sub>

```bash
mo2_lint update <directory> [options]
```

> #### Parameters
> `<directory>` is a required parameter.<br>
> Where `<directory>` is the path of the MO2 instance you want to update. Like the `pin` command, you must provide the exact path to the instance you wish to update. Higher level directories will not work for this command.

## The Instance State File
MO2-LINT maintains a state file that keeps track of all Mod Organizer 2 instances it manages. This file is located at `~/.config/mo2-lint/instance_state.json`.

When using the `install` commands, MO2-LINT will automatically update this state file to reflect the current instances. Similarly, when using the `uninstall` command, the corresponding instance will be removed from the state file, and `list` will read from this file to display the current instances.

It is imperative that this file is not modified manually, as it may lead to inconsistencies and errors when managing your MO2 instances.
