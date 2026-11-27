<img src="https://github.com/Furglitch/modorganizer2-linux-installer/raw/main/.github/README/logo.svg" alt="MO2-LINT Logo" width="96" align="left" />

# Mod Organizer 2 Linux Installer (MO2-LINT)

<br clear="left"/>

![GitHub Tag](https://img.shields.io/github/v/tag/Furglitch/modorganizer2-linux-installer?label=version) ![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/Furglitch/modorganizer2-linux-installer/total)

The **Mod Organizer 2 Linux Installer** (abbr. **MO2-LINT**) aims to make the installation process for [Mod Organizer 2] (MO2) on Linux systems easier and more accessible, offering a simple process to set up a fully functional MO2 instance along with additional quality-of-life features.

[Download](https://github.com/furglitch/modorganizer2-linux-installer/releases) | [Get Started](https://docs.furglitch.com/modorganizer2-linux-installer/getting-started/) | [View the TUI Guide](https://docs.furglitch.com/modorganizer2-linux-installer/tui-guide/) | [View the CLI Guide](https://docs.furglitch.com/modorganizer2-linux-installer/cli-guide/)<br/>

---

## Why MO2-LINT?

| | |
|:--|:--|
| **Totally Automated** | Sets up Proton, downloads MO2, registers compatibility tools, and establishes the `nxm://` protocol handler. |
| **Multiple Instances** | Run separate MO2 instances for each game, each independently tracked and updatable. |
| **Easy-to-Use** | Provides a simple terminal-based UI (TUI), as well as CLI commands, for quick and easy installation. |
| **Nexus Integration** | The bundled `nxm://` protocol handler makes the "Mod Manager Download" button on Nexus Mods work out of the box. |
| **Script Extenders** | Optionally install the game's script extender (SKSE, F4SE, etc.) during setup. |
| **MO2 Plugins & Themes** | Optionally install community plugins and themes for Mod Organizer during setup. |
| **Compatibility Workarounds** | Ships fixes for known Proton/Wine quirks per game, so you don't have to hunt them down yourself. |

### Supported Games, Plugins, and Themes

See the [Compatibility] page for the full list of games, MO2 plugins, and themes that MO2-LINT can set up. Check the [Game Guides] too, as some games need extra steps before or after `install`.

## Where to go next

Check out the documentation at [docs.furglitch.com](https://docs.furglitch.com/modorganizer2-linux-installer/) for more information.

- **New here?** Start with [Getting Started], which covers prerequisites, installing the binary, setting up Proton, and the first `install`.
- **Prefer menus over commands?** The [TUI Guide] walks through the interactive interface.
- **Already installed?** Jump to the [CLI Guide] for every command and option.
- **Installing a specific game?** Check [Game Guides] for per-game notes before you run `install`.
- **Something not working?** Head to [Troubleshooting] or the [FAQ].
- **Want to help?** See [Contributing] to learn how to get involved with the project.

## Credits

The *Mod Organizer 2 Linux Installer* was originally developed by [rockerbacon](https://github.com/rockerbacon) as a Bash script. After version 5.0.3, development was handed over to [Furglitch](https://github.com/furglitch), who has since fully rewritten it in Python for maintainability, extensibility, and cross-distro compatibility.

[Getting Started]: https://docs.furglitch.com/modorganizer2-linux-installer/getting-started/
[TUI Guide]: https://docs.furglitch.com/modorganizer2-linux-installer/tui-guide/
[CLI Guide]: https://docs.furglitch.com/modorganizer2-linux-installer/cli-guide/
[Game Guides]: https://docs.furglitch.com/modorganizer2-linux-installer/game-guide/
[Compatibility]: https://docs.furglitch.com/modorganizer2-linux-installer/resources/
[Troubleshooting]: https://docs.furglitch.com/modorganizer2-linux-installer/troubleshooting/
[FAQ]: https://docs.furglitch.com/modorganizer2-linux-installer/faq/
[Contributing]: https://docs.furglitch.com/modorganizer2-linux-installer/contributing/
