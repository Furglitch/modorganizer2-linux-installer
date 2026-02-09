---
title: Installation
layout: default
nav_order: 1
parent: Installation and Usage
---

# Installing MO2-LINT

Installation of MO2-LINT is straightforward. Follow the steps below to get started.

Download the latest release from the [GitHub Releases page]. The file is called `mo2-lint` (without any file extension).
<sub>Please note, only versions above 7.0.0 are supported.</sub>

Make the downloaded file executable. You can do this via the terminal with the command:
```bash
chmod +x path/to/downloaded/mo2-lint
```

After making the file executable, you can run MO2-LINT directly from the terminal:
```bash
path/to/downloaded/mo2-lint <command> [options]
```

### Setting up Proton

Proton is required for MO2-LINT to function properly. Currently, MO2-LINT is tested with Proton 10 and only supports that version, though older versions may work.

You can set up Proton with the below steps. These steps are also given during the installation process.

#### Steam:

> #### Option A: Universal Settings
> 1. In the Steam settings (not the individual game settings), navigate to the 'Compatibility' section.
> 2. Set the 'Default compatibility tool' to 'Proton 10'.
> *This will make all Steam games use Proton 10 by default*.
>
> #### Option B: Per-Game Settings
> If you prefer using a different Proton version by default, you can set Proton 10 for specific games.
> 1. Right-click on the game in your Steam library.
> 2. Select 'Properties', and navigate to the 'Compatibility' tab.
> 3. Check the box for 'Force the use of a specific Steam Play compatibility tool', if it's not already checked.
> 4. From the dropdown menu, select your preferred Proton version. Proton 10.0 is the supported and recommended version.
> 5. Close the properties window.
>
> **After setting up Proton**, make sure to launch the game at least once to allow Steam to set up the Proton prefix with the default dependencies, as these are not included with MO2-LINT and need to be set up by Steam.

#### Heroic (GOG and Epic):

> ### Option A: Universal Settings
> 1. In Heroic, navigate to 'Settings', then the 'Game Defaults' section.
> 2. Under 'Wine Version', select 'Proton - Proton 10.0' from the dropdown menu.
> *This will make all games launched through Heroic use Proton 10 by default*.
>
> ### Option B: Per-Game Settings
> If you prefer using a different Proton version by default, you can set Proton 10 for specific games.
> 1. Right-click on the game in your Heroic library.
> 2. Select 'Settings' and navigate to the 'Wine' tab.
> 3. Under 'Wine Version', select 'Proton - Proton 10.0' from the dropdown menu.
>
> ### Notes for either option:
> - If you don't see Proton versions in the dropdown, you may need to go to Heroic's settings, navigate to the 'Advanced' tab, and enable 'Allow using Valve Proton builds to run games'.
> - In Heroic's settings, you can navigate to 'Game Defaults' section, the 'Other' tab, and enable 'Use Steam Runtime'. This is recommended and may help with compatibility.

### Installing to PATH (Optional)

It is recommended to move the executable to a directory included in your system's PATH, such as `/usr/local/bin`, for easier access:
```bash
sudo mv path/to/downloaded/mo2-lint /usr/local/bin/mo2-lint
```
If you are not sure what directories are in your PATH, you can check by running:
```bash
echo "$PATH" | tr ':' '\n'
```

You can now run MO2-LINT from the terminal by simply typing:
```bash
mo2-lint <command> [options]
```

For detailed usage instructions, refer to the [Usage](../usage/) page.

[GitHub Releases page]: https://github.com/furglitch/modorganizer2-linux-installer/releases
