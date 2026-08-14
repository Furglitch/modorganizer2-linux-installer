---
title: FAQ
layout: default
nav_order: 6
description: "Frequently asked questions about MO2-LINT."
---

# Frequently Asked Questions

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## General

**What is MO2-LINT?**

MO2-LINT (Mod Organizer 2 Linux Installer) automates installing and configuring [Mod Organizer 2](https://github.com/Modorganizer2/modorganizer) on Linux. It handles Proton prefix setup, Steam/Heroic launch option configuration, `nxm://` protocol registration, and optional plugin and script extender installation.

**Is Mod Organizer 2 itself included?**

No, a copy of MO2 is not bundled into MO2-LINT. MO2-LINT downloads and installs the latest MO2 automatically when you run `install`. You don't need to download it separately.

**What launchers are supported?**

- **Steam** - fully supported
- **Heroic Games Launcher** - supported for GOG and Epic Games Store titles

**Can I have multiple MO2 instances?**

Yes. Each `mo2-lint install` creates a separate, independent instance, including multiple instances of the same game. However, Nexus' "Mod Manager Download" button can only target one instance per game at a time; installing a second instance of the same game prompts you to confirm switching the NXM handler link to it.

## Installation

**Which version of Proton should I use?**

Proton 11.0 is the only officially tested and supported version. Earlier versions may work but aren't guaranteed. See [Setting up Proton](../getting-started/proton-setup).

**Do I need to launch the game before running MO2-LINT?**

Yes, at least once through Steam or Heroic, so the launcher can initialize the Proton prefix MO2-LINT depends on.

**I'm getting a "game not found" error. What do I do?**

MO2-LINT locates games by searching your Steam or Heroic library. Common causes:

- The game hasn't been launched yet (Proton prefix not initialized)
- It's installed in a non-standard library location
- You're using an unsupported launcher
- You're using a non-standard install (e.g. a cracked version with a non-native shortcut)
- You're using a sandboxed launcher (e.g. Flatpak Steam) without the proper permissions

See [Installation Issues](../troubleshooting/installation-issues#game-not-found) for the full walkthrough.

## Tips and tricks

**How do I get MO2 to only open in Desktop Mode on Steam Deck?**

Add this to the game's launch options to skip MO2 in Gaming/Big Picture mode while still opening it in Desktop Mode:

```
%command% $([ -z "$KDE_FULL_SESSION" ] && echo 'moshortcut://"SKSE"' )
```

{: .warning }
> Only SteamOS environments are supported.

{: .note }
> Written prior to the Steam Machine/Steam Frame release, so may need adjustment once those are available. If you are using a Steam Machine or Steam Frame, please report your findings to the [GitHub Issues](https://github.com/furglitch/modorganizer2-linux-installer/issues) page.

## Troubleshooting

**Where are the log files?**

`~/.cache/mo2-lint/logs/`. Include these when reporting issues.

**MO2 launches but immediately closes. What should I do?**

Usually a launch settings problem. See [Launch & Proton Issues](../troubleshooting/launch-issues).

**Something broke after updating MO2-LINT. What should I do?**

Run `mo2-lint update /path/to/instance` to refresh the instance with the new version's configuration. If it persists, check [GitHub Issues](https://github.com/furglitch/modorganizer2-linux-installer/issues) or open a new report with your log files attached.
