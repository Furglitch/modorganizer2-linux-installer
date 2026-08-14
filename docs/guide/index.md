---
title: CLI Guide
layout: default
nav_order: 3
has_children: true
description: "Command reference and configuration for MO2-LINT."
---

# CLI Guide

{: .note }
> Read through [Game Guides](../game-guides/) for your game before running `install`. Some games need extra steps.

Every MO2-LINT command accepts these two global options:

| Flag | Short | Description |
|:--|:--|:--|
| `--log-level <level>` | `-l` | Controls log verbosity in the console: `DEBUG`, `INFO`, or `TRACE`. Log files will always be `TRACE`. |
| `--unattended` | `-u` | Skips interactive prompts and uses defaults. |

## Commands

| Command | Purpose |
|:--|:--|
| [`install`](./install) | Create a new MO2 instance for a game. |
| [`update`](./update) | Refresh an existing instance's MO2 build and launch option. |
| [`uninstall` / `list` / `pin` / `unpin`](./managing-instances) | Remove, list, and lock instances. |

## Reference

| Page | Covers |
|:--|:--|
| [Configuration](./configuration) | `settings.toml` and the instance state file. |
| [Themes](./themes) | Applying built-in and Nexus themes, plus desktop-matching themes. |
| [Custom Games](./custom-games) | Advanced/unsupported `--custom` game definitions. |
