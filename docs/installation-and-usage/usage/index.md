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

Where `<game>` is the game you want to install MO2 for (e.g., `skyrim`, `fallout4`), and `<directory>` is the path where you want the MO2 instance to be created.<br>
Supported games can be seen by running:
```bash
mo2_lint install --help
```

## `uninstall`
The `uninstall` command removes an existing Mod Organizer 2 instance. Specifying the game and/or directory is not required, but can help target the correct instance.
```bash
mo2_lint uninstall <game> <directory> [options]
```

Given `<game>`, the script will look for MO2 instances associated with that game.<br>
If `<directory>` is provided, it will specifically target the MO2 instance located at that path. You can also use higher level directories to search for instances within it's subdirectories.

## `list`
The `list` command displays all Mod Organizer 2 instances currently managed by MO2-LINT. Specifying the game and/or directory is not required, but can help target the correct instance.
```bash
mo2_lint list <game> <directory> [options]
```

Given `<game>`, the script will filter and display only MO2 instances associated with that game.<br>
If `<directory>` is provided, it will specifically look for MO2 instances located at that path. You can also use higher level directories to search for instances within it's subdirectories.

## The Instance State File
MO2-LINT maintains a state file that keeps track of all Mod Organizer 2 instances it manages. This file is located at `~/.config/mo2-lint/instance_state.json`.

When using the `install` commands, MO2-LINT will automatically update this state file to reflect the current instances. Similarly, when using the `uninstall` command, the corresponding instance will be removed from the state file, and `list` will read from this file to display the current instances.

It is imperative that this file is not modified manually, as it may lead to inconsistencies and errors when managing your MO2 instances.
