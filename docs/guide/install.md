---
title: install
layout: default
nav_order: 1
parent: CLI Guide
---

# `install`

Creates a new Mod Organizer 2 instance for the specified game.

```bash
mo2-lint install <game> <directory> [options]
```

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Parameters

| Parameter | Required | Description |
|:--|:--|:--|
| `<game>` | Required | The game identifier (e.g. `skyrim`, `fallout3_goty`).<br/>Run `mo2-lint install --help` for the full list. |
| `<directory>` | Optional | Where the instance is created.<br/>If omitted, MO2-LINT builds a path from `~/.config/mo2-lint/settings.toml` (`[instance.folders]`, see [Configuration](./configuration)). If the directory already exists, it must be empty. |

## Options

`--plugin <plugin>`, `-p <plugin>`
: Install a plugin into the new instance. Repeatable:
  ```bash
  mo2-lint install skyrim /path/to/instance -p root-builder -p nxm-collection-dl
  ```
  Run `mo2-lint install --help` for available plugins. A default list can be set via `[instance].plugins` in `settings.toml`.

`--script-extender`, `-s`
: Install the game's script extender (e.g. SKSE, F4SE), if one exists. Prompts if multiple versions are available. Ignored for games with no script extender. If Root Builder is installed, it will automatically use that method to install the script extender.

`--launcher <launcher>`, `-L <launcher>`
: Force `steam`, `gog`, or `epic` instead of auto-detecting. Default settable via `[instance].launcher`. If not specified, MO2-LINT will prompt the user to choose if multiple launchers are detected.

`--theme <name>`, `-t <name>`
: Apply a theme to the new instance. See [Themes](./themes). Default settable via `[instance].theme`.

`--custom <path/to/file.yml>`
: [Unsupported / Advanced] Use a custom game info file. See [Custom Games](./custom-games).

`--mo2-archive <path>` + `--mo2-checksum <sha256>`
: [Unsupported / Advanced] Install MO2 from a local `.zip`/`.7z` archive instead of downloading the bundled version. Both flags are required together. The archive is verified against the checksum before extraction. Useful for offline installs or pinning a specific build.
  ```bash
  mo2-lint install skyrim /path/to/instance \
    --mo2-archive ~/Downloads/Mod.Organizer-2.5.2.7z \
    --mo2-checksum <sha256>
  ```
  The instance is automatically [pinned](./managing-instances#pin) afterward, so a later `update` won't overwrite your chosen build.

## After installing

At the end of the installation process, MO2-LINT will print instructions for launching the new instance. The instructions vary depending on the detected launcher (Steam, GOG, or Epic).

You can proceed to step 3 of the [First Launch](../getting-started/first-launch#3-launch-through-steam-or-heroic) guide.
