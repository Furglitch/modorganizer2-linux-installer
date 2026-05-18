---
title: FAQ
layout: default
nav_order: 5
parent: Mod Organizer 2 Linux Installer
---

# Frequently Asked Questions

## General

### What is MO2-LINT?

MO2-LINT (Mod Organizer 2 Linux Installer) automates the installation and configuration of [Mod Organizer 2](https://github.com/Modorganizer2/modorganizer) on Linux. It handles Proton prefix setup, Steam/Heroic launch option configuration, registration of the nxm:// protocol, and optional plugin and script extender installation.

### Is Mod Organizer 2 itself included?

No. MO2-LINT downloads and installs the latest version of Mod Organizer 2 automatically when you run the `install` command. You do not need to download MO2 separately.

### What launchers are supported?

- **Steam** - fully supported
- **Heroic Games Launcher** - supported for GOG and Epic Games Store titles

### Can I have multiple MO2 instances?

Yes. Each `mo2-lint install` creates a separate, independent instance. For technical reasons, instances are currently limited to one per game.

---

## Installation

### Which version of Proton should I use?

Proton 10.0 is the only officially tested and supported version. Earlier versions may work but are not guaranteed. See [Setting up Proton](../installation/#setting-up-proton) for step-by-step setup instructions.

### Do I need to launch the game before running MO2-LINT?

Yes. Launch the game at least once through Steam or Heroic before running `mo2-lint install`. This allows the launcher to initialize the Proton prefix that MO2-LINT requires.

### I'm getting a "game not found" error during install. What do I do?

MO2-LINT locates games by searching your Steam or Heroic library. Common causes:

- The game has not been launched yet (Proton prefix not initialized)
- The game is installed in a non-standard library location
- You are using a launcher that is not supported
- You are using a non-standard installation of the game (e.g. cracked version with a non-native launch shortcut)

Verify the game is visible in your launcher and has been launched at least once. If it is installed in a non-standard location, check that the launcher knows about that library path.

---

## Troubleshooting

### Where are the log files?

Logs are stored at `~/.cache/mo2-lint/logs/`. Include these when reporting issues.

### MO2 launches but immediately closes. What should I do?

This is usually a launch settings problem. See the [Troubleshooting](../troubleshooting/) page for common causes, including `gamemoderun` interference and Flatpak Steam permission issues.

### Something broke after updating MO2-LINT. What should I do?

Run `mo2-lint update /path/to/instance` to refresh the instance with the new version's configuration. If the problem persists, check the [GitHub Issues](https://github.com/furglitch/modorganizer2-linux-installer/issues) page or open a new report with your log files attached.
