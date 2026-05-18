## Introduction

This project aims to make modding and playing Bethesda games on Linux as easy as possible. It does that by providing installers which automatically setup a working experience for the user.

While these installers may be available on Lutris.net, users are always recommended to use the latest stable release from this repository. The testers and maintainers of this project have little control over the content on Lutris and cannot assure that the installers available there are up to date nor that they haven't been incorrectly modified.

## Installing Mod Organizer 2

#### Requirements

You may need to manually install the following programs:

- _7z_
    - Should be readily available in your distribution's package manager
- _protontricks_
    - **Steam Deck users**: Protontricks must be installed through the Discover app.
    - **Other distributions**: carefully read through the [available install methods](https://github.com/Matoking/protontricks#installation) to ensure you're using an up-to-date version of the program.

The following requirements should be available out-of-the-box in most systems:

- _bash_
- either _curl_ or _wget_
- _zenity_
- _protontricks-launcher_: should be available after installing `protontricks` already, if not see [this](https://github.com/Matoking/protontricks#desktop)

#### Installation steps

1. Install the game you want to play on Steam;
2. Download the the latest stable release [here](https://github.com/rockerbacon/modorganizer2-linux-installer/releases/download/5.0.3/mo2installer-5.0.3.tar.gz);
3. Extract the downloaded file;
4. Open the extracted folder in a terminal and execute `./install.sh`;
5. The installer will start and guide you through the rest of the process;
6. Run the game on Steam and Mod Organizer 2 should start;
7. Read the [post-install instructions](post-install.md) for recommended additional steps;

The installer will automatically configure game-specific workarounds and install the script extender for your game of choice. Java binaries are also made available at `C:\java` for running Proc Patchers.

**Avoid using ENBoost** with Skyrim: DXVK and Wine have their own better working memory patches, both properly enabled with this installer.

### Features

The following is a small overview of the current state of each supported game:

| GAME                   | GAMEPLAY      | SCRIPT EXTENDER           | ENB           |
| :--------------------- | :------------ | :------------------------ | :------------ |
| Fallout 3              | working | working                | not tested    |
| Fallout 4              | working | [some plugins might not work](https://github.com/rockerbacon/lutris-skyrimse-installers/issues/32) | ENB v0.393 or older, disabling "EnablePostPassShader" might be necessary |
| Fallout New Vegas      | fullscreen only       | working | working    |
| Morrowind              | not tested    | not tested                | not tested    |
| Oblivion               | working    | [some plugins might require manual setup](https://github.com/rockerbacon/lutris-skyrimse-installers/issues/63#issuecomment-643690247)                 | not tested    |
| Skyrim                 | working       | working                   | working       |
| Skyrim Special Edition | working       | working                   | not tested |
| Starfield              | working       | working                   | not tested |

For known bugs and necessary workarounds, please refer to the [issues page](https://github.com/rockerbacon/lutris-skyrimse-installers/issues?q=is:issue+is:open+label:bug+)

Please, help to keep this table up to date by [opening issues](https://github.com/rockerbacon/lutris-skyrimse-installers/issues/new/choose) on any successes or problems you have experienced.

## Updating Mod Organizer 2

It is highly recommended to backup your existing installation before updating.

#### From 5.0.0 and above

You can update by simply following the install instructions again.

#### From 4.X.X and below

Version 5 of the installer updates ModOrganizer to version 2.5, which cannot be applied on top of an existing 2.4.4 instance. Users with working 4.X.X (or older) installations are recommended to not update.

Advanced users may reference the [ModOrganizer 2.5.0 release page](https://github.com/ModOrganizer2/modorganizer/releases/tag/v2.5.0) for instructions on updating portable instances. There are no instructions for updating global instances, and this project has no plans on taking responsibility for such documentation.

#### From 3.1.0 and below

You can update by simply following the install instructions again.

If you have multiple instances installed, you'll need to update all of them for Nexus integration to work.

#### From 2.8.6 and below (old Lutris installer)

1. Go to where Mod Organizer was installed and rename the folder "ModOrganizer2" to "modorganizer2" (all lowercase);
2. Follow the install instructions in this readme;
3. If you have multiple instances installed, you'll need to update all of them for Nexus integration to work;

## Installing Vortex

The Vortex installer was created before Wine had builtin support for Mod Organizer 2. It should only be used for games which Mod Organizer 2 does not support.

The Vortex installer does not apply any configurations to the games themselves. Make sure they are working, using Lutris or another method, before modding. GAMES SHOULD NOT BE LAUNCHED FROM WITHIN VORTEX.

The Vortex installer is not under active development/maintenance at the moment.

To install Vortex, you first need the `vortex.yml` installer from the [latest release which included it](https://github.com/rockerbacon/lutris-skyrimse-installers/releases/tag/1.9.3).

You can use the installer with the following terminal command, remember to change the path if the file was downloaded to another location:
```bash
lutris -i "$HOME/Downloads/vortex.yml"
```

Remember to follow all instructions during installation, some manual steps are required for Vortex to work properly.

After installing Vortex and following all instructions, manually add the game you want to mod.

#### Notes

- The old Skyrim Special Edition and SKSE64 installers have been deprecated as the Mod Organizer 2 installer replaces both
- Advanced instructions for using Vortex can be found on [older versions of this README](https://github.com/rockerbacon/lutris-skyrimse-installers/tree/0203cd1fdc9832152ae1d87c488c7492ea3ecc61). They were removed since they are only applicable to games supported by the Mod Organizer 2 installer
