---
title: Mod Organizer 2 Linux Installer
layout: default
nav_order: 1
has_children: true
---

<img src="https://github.com/Furglitch/modorganizer2-linux-installer/raw/main/.github/README/logo.svg" alt="MO2-LINT Logo" width="96" align="left" />

# Mod Organizer 2 Linux Installer (MO2-LINT)

<br clear="left"/>

MO2-LINT aims to make installing [Mod Organizer 2](https://github.com/ModOrganizer2/modorganizer) on Linux systems easier and more accessible, providing a simple process to set up a fully functional Mod Organizer 2 installation with minimal user input.

[Get Started](./getting-started/){: .btn .btn-primary .mr-2 }
[View the CLI Guide](./guide/){: .btn .mr-2 }
[GitHub Releases](https://github.com/furglitch/modorganizer2-linux-installer/releases){: .btn .mr-2 }

---

## Why MO2-LINT?

| | |
|:--|:--|
| **Totally Automated** | `mo2-lint install` sets up Proton, downloads MO2, registers compatibility tools, and wires up the NXM handler. |
| **Multiple Instances** | Run separate MO2 instances for each game, each independently tracked and updatable. |
| **Easy-to-Use** | The CLI interface is designed to be as user friendly as possible, with clear commands and options. |
| **Nexus Integration** | The bundled NXM handler makes the "Mod Manager Download" button on Nexus Mods work out of the box. |
| **Script Extenders** | Optionally install the game's script extender (SKSE, F4SE, etc.) during setup. |
| **MO2 Plugins & Themes** | Optionally install community plugins and themes for Mod Organizer during setup. |
| **Compatibility Workarounds** | Ships fixes for known Proton/Wine quirks per-game, so you don't have to hunt them down yourself. |

### Supported Games

<br clear="left"/>
{: .fs-1 }

<details open markdown="1">
<summary>Click to collapse the compatibility table</summary>

| Game | Notes |
|:--|:--|
| Baldur's Gate 3 | |
| Cyberpunk 2077 | See [Game Guide](./game-guides/cyberpunk-2077/) |
| Dragon Age: Origins - Ultimate Edition | |
| Dragon Age 2 - Ultimate Edition | |
| Enderal: Forgotten Stories | |
| Enderal: Forgotten Stories - Special Edition | |
| Fallout 3 | |
| Fallout 3 - Game of the Year Edition | See [Game Guide](./game-guides/fallout-3-goty/) |
| Fallout 4 | See [Game Guide](./game-guides/fallout-4/) |
| Fallout 4 VR | |
| Fallout London | See [Game Guide](./game-guides/fallout-london/) |
| Fallout New Vegas | |
| Morrowind | |
| Oblivion | See [Game Guide](./game-guides/oblivion/) |
| Skyrim | |
| Skyrim Special Edition | |
| Skyrim VR | |
| Starfield | |
| Subnautica | |
| Valheim | |
| The Witcher 3: Wild Hunt | |
| The Witcher 3: Wild Hunt - Game of the Year Edition | |

</details>

{: .note }
> Setting up a specific game? Check the [Game Guides] section first. Some games need extra steps before or after `install`.

## Where to go next

- **New here?** Start with [Getting Started], which covers prerequisites, installing the binary, setting up Proton, and the first `install`.
- **Already installed?** Jump to the [CLI Guide] for every command, option, and file configuration.
- **Installing a specific game?** Check [Game Guides] for per-game notes before you run `install`.
- **Something not working?** Head to [Troubleshooting] or the [FAQ].
- **Want to help?** See [Contributing] to learn how to get involved with the project.

## Credits

Originally developed by [rockerbacon](https://github.com/rockerbacon) as a Bash script, MO2-LINT has since been maintained by [furglitch](https://github.com/furglitch) and fully rewritten in Python for maintainability, extensibility, and cross-distro compatibility.

[Getting Started]: ./getting-started/
[CLI Guide]: ./guide/
[Game Guides]: ./game-guides/
[Troubleshooting]: ./troubleshooting/
[FAQ]: ./faq/
[Contributing]: ./contributing/
