<img src="https://github.com/Furglitch/modorganizer2-linux-installer/raw/main/.github/README/logo.svg" alt="MO2-LINT Logo" width="96" align="left" />

# Mod Organizer 2 Linux Installer (MO2-LINT)

<br clear="left"/>

![GitHub Tag](https://img.shields.io/github/v/tag/Furglitch/modorganizer2-linux-installer?label=version) ![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/Furglitch/modorganizer2-linux-installer/total)

MO2-LINT aims to make installing [Mod Organizer 2](https://github.com/ModOrganizer2/modorganizer) on Linux systems easier and more accessible, providing a simple process to set up a fully functional Mod Organizer 2 installation with minimal user input.

[Get Started](https://docs.furglitch.com/modorganizer2-linux-installer/getting-started/) | [View the CLI Guide](https://docs.furglitch.com/modorganizer2-linux-installer/guide/) | [GitHub Releases](https://github.com/furglitch/modorganizer2-linux-installer/releases)<br/>

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

Games that MO2-LINT officially supports setting up instances for.

<details open markdown="1">
<summary>Click to collapse the game table</summary>

| MO2-LINT Slug | Game | Notes |
|:--|:--|:--|
| `baldursgate3` | Baldur's Gate 3 | |
| `cyberpunk2077` | Cyberpunk 2077 | See [Game Guide](https://docs.furglitch.com/modorganizer2-linux-installer/game-guides/cyberpunk-2077.html) |
| `dragonage` | Dragon Age: Origins - Ultimate Edition | |
| `dragonage2` | Dragon Age 2 - Ultimate Edition | |
| `enderal` | Enderal: Forgotten Stories | |
| `enderal_se` | Enderal: Forgotten Stories - Special Edition | |
| `fallout3` | Fallout 3 | |
| `fallout3_goty` | Fallout 3 - Game of the Year Edition | See [Game Guide](https://docs.furglitch.com/modorganizer2-linux-installer/game-guides/fallout-3-goty.html) |
| `fallout4` | Fallout 4 | See [Game Guide](https://docs.furglitch.com/modorganizer2-linux-installer/game-guides/fallout-4.html) |
| `fallout4_vr` | Fallout 4 VR | |
| `falloutlondon` | Fallout London | See [Game Guide](https://docs.furglitch.com/modorganizer2-linux-installer/game-guides/fallout-london.html) |
| `falloutnv` | Fallout New Vegas | |
| `morrowind` | Morrowind | |
| `oblivion` | Oblivion | See [Game Guide](https://docs.furglitch.com/modorganizer2-linux-installer/game-guides/oblivion.html) |
| `skyrim` | Skyrim | |
| `skyrim_se` | Skyrim Special Edition | |
| `skyrim_ae` | Skyrim Anniversary Edition (Heroic) | See [Game Guide](https://docs.furglitch.com/modorganizer2-linux-installer/game-guides/skyrim-ae-heroic.html) |
| `skyrim_vr` | Skyrim VR | |
| `starfield` | Starfield | |
| `subnautica` | Subnautica | |
| `valheim` | Valheim | |
| `witcher3` | The Witcher 3: Wild Hunt | |
| `witcher3_goty` | The Witcher 3: Wild Hunt - Game of the Year Edition | |

</details>

{: .note }
> Check the [Game Guides] section first. Some games need extra steps before or after `install`.

### Available Plugins

MO2 Plugins available for automatic install using the `--plugin <slug>` flag

<details open markdown="1">
<summary>Click to collapse the plugin table</summary>

| MO2-LINT slug | Author | URL |
|:--|:--|:--|
| `root-builder` | Kezyma | [Kezyma/Modorganizer-Plugins] |
| `reinstaller` | Kezyma | [Kezyma/Modorganizer-Plugins]|
| `shortcutter` | Kezyma | [Kezyma/Modorganizer-Plugins]|
| `plugin-finder` | Kezyma | [Kezyma/Modorganizer-Plugins]|
| `profile-sync` | Kezyma | [Kezyma/Modorganizer-Plugins]|
| `openmw-player` | Kezyma | [Kezyma/Modorganizer-Plugins]|
| `grass-precacher` | Al12rs | [Al12rs/modorganizer-GrassPrecacher](https://github.com/Al12rs/modorganizer-GrassPrecacher) |
| `auto-activator` | Jonathan Feenstra | [JonathanFeenstra/modorganizer-auto-activator](https://github.com/JonathanFeenstra/modorganizer-auto-activator) |
| `fomod-plus` | aglowinthefield | [aglowinthefield/mo2-fomod-plus](https://github.com/aglowinthefield/mo2-fomod-plus) |
| `collection-installer` | RGM2025 | [Nexus Mods](https://www.nexusmods.com/site/mods/2350)

</details>

## Where to go next

Check out the documentation at [docs.furglitch.com](https://docs.furglitch.com/modorganizer2-linux-installer/) for more information.

- **New here?** Start with [Getting Started], which covers prerequisites, installing the binary, setting up Proton, and the first `install`.
- **Already installed?** Jump to the [CLI Guide] for every command, option, and file configuration.
- **Installing a specific game?** Check [Game Guides] for per-game notes before you run `install`.
- **Something not working?** Head to [Troubleshooting] or the [FAQ].
- **Want to help?** See [Contributing] to learn how to get involved with the project.

## Credits

Originally developed by [rockerbacon](https://github.com/rockerbacon) as a Bash script, MO2-LINT has since been maintained by [furglitch](https://github.com/furglitch) and fully rewritten in Python for maintainability, extensibility, and cross-distro compatibility.

[Getting Started]: https://docs.furglitch.com/modorganizer2-linux-installer/getting-started/
[CLI Guide]: https://docs.furglitch.com/modorganizer2-linux-installer/guide/
[Game Guides]: https://docs.furglitch.com/modorganizer2-linux-installer/game-guides/
[Troubleshooting]: https://docs.furglitch.com/modorganizer2-linux-installer/troubleshooting/
[FAQ]: https://docs.furglitch.com/modorganizer2-linux-installer/faq/
[Contributing]: https://docs.furglitch.com/modorganizer2-linux-installer/contributing/

[Kezyma/ModOrganizer-Plugins]: https://github.com/Kezyma/ModOrganizer-Plugins
