<img src="https://github.com/Furglitch/modorganizer2-linux-installer/raw/main/.github/README/logo.svg" alt="MO2-LINT Logo" width="96" align="left" />

# Mod Organizer 2 Linux Installer (MO2-LINT)

<br clear="left"/>

Mod Organizer 2 Linux Installer (MO2-LINT, for short) aims to make installing [Mod Organizer 2] on Linux systems easier and more accessible, providing a simple process to set up a fully functional Mod Organizer 2 installation with minimal user input.

Originally developed by [rockerbacon][@rockerbacon] as a Bash script, it has since been maintained by [furglitch][@furglitch] and fully rewritten in Python to improve maintainability, extensibility, and cross-distro compatibility.

## Features
- Automated installation and removal of Mod Organizer 2 and its dependencies
- Support for multiple instances of Mod Organizer 2
- No additional installations required beyond the installer itself
- Easy-to-use command-line interface
- Automatic handling of the Nexus Mods 'Mod Manager Download' button via a custom NXM handler
- Automatic setup of various plugins for Mod Organizer 2
- Implements various workarounds to improve compatibility with certain mods

### Supported Games

| Game                     | Gameplay          | Script Extender                                          | ENB                                                            |
|:-------------------------|:------------------|:---------------------------------------------------------|:---------------------------------------------------------------|
| Cyberpunk 2077           | Working*          | N/A                                                      | Not Tested                                                     |
| Dragon Age: Origins      | Working*          | N/A                                                      | N/A                                                            |
| Enderal                  | Working*          | Working*                                                 | Working*                                                       |
| Enderal Special Edition  | Working*          | Working*                                                 | Not Tested                                                     |
| Fallout 3                | Working*          | Working*                                                 | Not Tested                                                     |
| Fallout 3 GOTY           | Working*          | Working*                                                 | Not Tested                                                     |
| Fallout 4                | Working*          | Some F4SE plugins may not work. See [#32]*               | ≤ v0.393 may need `EnablePostPassShader` disabled. See [#95]*  |
| Fallout London           | Not Tested        | Not Tested                                               | Not Tested                                                     |
| Fallout New Vegas        | Fullscreen Only*  | Working*                                                 | Working*                                                       |
| Morrowind                | Not Tested*       | Not Tested                                               | Not Tested                                                     |
| Oblivion                 | Working*          | Some xOBSE plugins may require manual setup. See [#63]*  | Not Tested                                                     |
| Skyrim                   | Working*          | Working*                                                 | Working*                                                       |
| Skyrim Special Edition   | Working*          | Working*                                                 | Working*                                                       |
| Starfield                | Working*          | Working*                                                 | Not Tested                                                     |

<sub>* Game last tested with a pre 7.0.0 version of MO2-LINT. Issues may arise, please report if you encounter any problems with a supported game.</sub><br>

## Getting Started
To get started with MO2-LINT, please refer to the [Installation Guide] for detailed instructions on how to install and use the installer.

## Contributing
Contributions to MO2-LINT are welcome! If you would like to contribute, please read the [Contributing Guide] for more information on how to get involved.



[Mod Organizer 2]: https://github.com/Modorganizer2/modorganizer
[@rockerbacon]: https://github.com/rockerbacon
[@furglitch]: https://github.com/furglitch

[Installation Guide]: https://wiki.furglitch.com/modorganizer2-linux-installer/installation/
[Contributing Guide]: https://wiki.furglitch.com/modorganizer2-linux-installer/contributing/

[#32]: https://github.com/furglitch/modorganizer2-linux-installer/issues/32
[#63]: https://github.com/furglitch/modorganizer2-linux-installer/issues/63#issuecomment-643690247
[#95]: https://github.com/furglitch/modorganizer2-linux-installer/issues/95
