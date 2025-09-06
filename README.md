# Mod Organizer 2 Linux Installer

> $${\color{red}Temporary \space Hold}$$<br/>
> This has been my main project for a number of months, and will currently be on the backburner while I focus on getting settled into a new job as well as work on other projects. Progress is halted unless a major update or bugfix is needed, but the project is not abandoned.

This project aims to installing Mod Organizer 2 instances on Linux as easy as possible. It does that by providing installers which automatically setup a working experience for the user. 

Originally developed by rockerbacon. A major thanks to him for doing most of the legwork.

## Installing Mod Organizer 2

### Requirements

_Currently only supports Steam installations._

| Program | Purpose | Availability |
|---------|---------|--------------|
| bash    | programming language | Installed by default on *most* distros |
| curl _or_ wget | internet downloads | Installed by default on *most* distros |
| zenity | dialog boxes ("gui") | Installed by default on *most* distros |
| 7z | archive extractor | Should be available through your distro's package manager |
| jq | json reader | Should be available through your distro's package manager.</br>Soft requirement for MO2 plugins, will run without it |
| protontricks | proton prefix editor | **Steam Deck:** Must install via Discover.</br>**Others:** Check [available install methods](https://github.com/Matoking/protontricks#installation) to ensure you're using an up-to-date version |
| protontricks-launcher | protontricks gui | Should come with `protontricks`. If it's not available, see [this](https://github.com/Matoking/protontricks#desktop)

### Installation Steps
1. Install the game you want to play on Steam;
2. Download the the latest stable release [here](https://github.com/furglitch/modorganizer2-linux-installer/releases/latest).
3. Extract the downloaded file;
4. Open the extracted folder in a terminal and execute `./install.sh`;
5. The installer will start and guide you through the rest of the process;
6. After installation, ***read the [post-install instructions](post-install.md)***. It contains additional recommended steps and required configurations for some games;
7. Run the game on Steam and Mod Organizer 2 should start;

The installer will automatically configure game-specific workarounds and install the script extender for your game of choice. Java binaries are also made available at `C:\java` for running Proc Patchers.

**Avoid using ENBoost** with Skyrim: DXVK and Wine have their own better working memory patches, both properly enabled with this installer.

**While these installers may be available on Lutris.net**, users are always recommended to use the latest stable release from this repository. The testers and maintainers of this project have little control over the content on Lutris and cannot assure that the installers available there are up to date nor that they haven't been incorrectly modified.

**To uninstall MO2**, follow the [uninstallation guide](uninstall.md).

## Supported Games
| Game                   | Gameplay          | Script Extender                                                                | ENB                                |
|------------------------|-------------------|--------------------------------------------------------------------------------|------------------------------------|
| Cyberpunk 2077         | Working           | N/A                                                                            | Not Tested                         |
| Dragon Age: Origins    | Working           | N/A                                                                            | N/A                                |
| Enderal                | Working           | Working                                                                        | Working                            |
| Enderal Special Edition| Working           | Working                                                                        | Not Tested                         |
| Fallout 3              | Working           | Working                                                                        | Not Tested                         |
| Fallout 3 GOTY         | Working           | Working                                                                        | Not Tested                         |
| Fallout 4              | Working           | Some plugins may not work. See [#32](https://github.com/Furglitch/modorganizer2-linux-installer/issues/32) | v0.393 or older might need `EnablePostPassShader` disabled  |
| Fallout New Vegas      | Fullscreen Only   | Working                                                                        | Working                            |
| Morrowind              | Not Tested        | Not Tested                                                                     | Not Tested                         |
| Oblivion               | Working           | Some plugins might require manual setup                                        | Not Tested                         |
| Oblivion Remastered*   | Not Tested        | N/A                                                                            | Not Tested                         |
| Skyrim                 | Working           | Working                                                                        | Working                            |
| Skyrim Special Edition | Working           | Working                                                                        | Working                            |
| Starfield              | Working           | Working, Not Included (Hosted on Nexus)                                        | Not Tested                         |

<sub>* Requires an in-dev version of MO2. This is available through the prerelease builds.</sub>

For known bugs and necessary workarounds, please refer to the [issues page](https://github.com/furglitch/modorganizer2-linux-installer/issues?q=is:issue+label:bug).</br>
Please, help to keep this table up to date by [opening issues](https://github.com/furglitch/modorganizer2-linux-installer/issues/new/choose) on any successes or problems you have experienced.

## Plugin Installation
_This feature is dependent on `jq` being installed, and will be skipped if it is not available._<br/>
The installer will give you a choice of MO2 plugins to automatically download and install. If you do not want to install any plugins, simply skip the plugin selection step.

Plugin information is loaded via the manifest system created by [Kezyma](https://github.com/Kezyma) and is up to plugin developers to maintain. To add a plugin to this project, add a link to the raw manifest file to [pluginsinfo.json](./pluginsinfo.json) Please refer to Keyzma's [documentation](https://kezyma.github.io/?p=pluginfinder#new-col) for more information on how to create a plugin manifest.

Compatibility with plugins is not guaranteed or supported. If you have issues with a plugin, please report it to the plugin developer.
If a plugin is found to be outdated or incompatible with Linux/Proton, it will be disabled/removed from the installer until it is fixed.

## Updating Mod Organizer 2

It is highly recommended to backup your existing installation before updating.

#### From 5.0 and above
You can update by simply following the install instructions again.

#### From 4.X.X and below
Instructions are included in the [archived README](.github/OLD-README.md#from-4xx-and-below). Installations of versions prior to 5.0.0 are not supported.

## Installing Vortex
The Vortex installer was created before Wine had builtin support for Mod Organizer 2. It should only be used for games which Mod Organizer 2 does not support.
Vortex installations are not supported. Instructions are only provided as a reference.
Instructions are included in the [archived README](.github/OLD-README.md#installing-vortex).
