---
title: Fallout London
layout: default
nav_order: 1
parent: Game-Specific Instructions
---

# Installing Fallout London

Fallout London is a mod for Fallout 4 that's only available via a GOG-provided installer. This means that the installation process is a bit different from other games.

### Prerequisites

- Make sure you have Fallout London added to your GOG library. As of writing (*20 March 2026*), the mod is available for free and can be claimed [here](https://www.gog.com/en/game/fallout_london).
- Download Fallout London from GOG, but *do not* run the installer yet.
- Download a *clean* copy of Fallout 4. Ensure you have version *1.10.163*, as this is **REQUIRED** for Fallout London.
  - The GOG version of Fallout 4 is recommended, as it is on *1.10.163* as of writing.
  - If you have the Steam version, you will need to downgrade it to *1.10.163* if you haven't already. There are a variety of guides and tools available online to help with this process.
  - Make sure to run the game at least once so the prefix files are generated and detectable by MO2-LINT.

### Installation Steps

#### Method 1: Direct Installation

1. Run the Fallout London installer you downloaded from GOG.
2. Click 'Install'.
3. If it hasn't automatically detected your Fallout 4 installation, click 'Change Location' and navigate to the Fallout 4 installation directory (not the Data folder, but the main folder containing `Fallout4.exe`).
   - Note: The built-in file browser can be buggy and is known to double-click folders, resulting in you having to navigate back up to the correct directory. Be patient and careful when navigating.
4. Run the installer and wait for it to finish. It may take a while, so be patient.
5. Once the installation is complete, you can proceed to set up MO2-LINT for Fallout London.
   - Note: Fallout London already includes F4SE, do **NOT** use the `-s` or `--script-extender` option when setting up MO2-LINT for Fallout London.
   ```bash
   mo2-lint install falloutlondon
   ```

#### Method 2: Installation via Mod Organizer 2 (Slightly Advanced)

1. Run MO2-LINT with the `-s` or `--script-extender` option to set up a new profile for Fallout London. For example:
   ```bash
   mo2-lint install falloutlondon -s
   ```
   - In contrast to the direct installation method, you **must** use the `-s` or `--script-extender` option with this method. This is because the GOG installer itself does not include F4SE, but rather downloads it during installation.
   - Optionally, you can install F4SE as a Root Builder mod by adding the `-p root-builder` option. This will keep your Fallout 4 installation clean.
- Optional: Set variables for easier copy-pasting. It can make the process easier. Example commands will use these variables, but you can also just replace the paths in the commands with the actual paths if you prefer.
  ```bash
  export INSTALLER_DIR='<path/to/installer>' # Fallout London download directory
  export MO2_DIR='<path/to/mo2>' # Mod Organizer 2 instance directory
  ```
2. Run Mod Organizer once to create the profile. When setting up the profile, ensure you have 'Use Profile-Specific INI Files' enabled. You can choose to enable 'Use Profile-Specific Save Games' as well, but this is optional.
3. In your file explorer, open both the MO2 instance directory and the Fallout London installer directory.
4. Copy the `Data` folder from the Fallout London installer directory to MO2's `mods` folder. You can rename the folder to something like `Fallout London` if you wish.
   ```bash
   mkdir -p "$MO2_DIR/mods/Fallout London"
   cp -r "$INSTALLER_DIR/Data"/* "$MO2_DIR/mods/Fallout London"
   ```
5. Copy the contents of the `__AppData` and `__Config` folders from the Fallout London installer directory to MO2's profile directory (i.e. `profiles/Default`). You will likely need to make the filenames lowercase to match MO2's expected filenames.
   ```bash
   for f in "$INSTALLER_DIR/__AppData/"* "$INSTALLER_DIR/__Config/"*; do
      cp -v "$f" "$MO2_DIR/profiles/Default/$(basename "$f" | tr '[:upper:]' '[:lower:]')"
   done
   ```
6. Open MO2 and enable the Data mod, or whatever you named the folder in Step 4. If you installed F4SE as a Root Builder mod, make sure to enable that as well.
7. You can now run Fallout London through MO2.
