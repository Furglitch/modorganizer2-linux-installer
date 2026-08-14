---
title: First Launch
layout: default
nav_order: 4
parent: Getting Started
---

# First Launch

A quick checklist to confirm your first instance is set up correctly.

## 1. Launch the game once (if you haven't already)

Before running `mo2-lint install`, you must start the game through Steam or Heroic at least once and let it load to the main menu, or the launcher if applicable. This initializes the Proton prefix that MO2-LINT depends on.

## 2. Create your instance

```bash
mo2-lint install <game> <directory>
```

To see what games are supported, run `mo2-lint install --help`. You can also see the [`install` command reference](../guide/install.html) for the full list of options (plugins, script extender, themes, custom archives).

## 3. Launch through Steam or Heroic

{: .warning }
> Always launch MO2 **through Steam or Heroic**, not by running the executable directly through Wine or Protontricks. MO2-LINT registers a launch option in your launcher; running the binary manually skips Proton/prefix setup entirely.

After installing, launch the game through your launcher. You should see a **"Launch Mod Organizer"** entry alongside the game's default launch option.

## 4. Confirm it worked

- Mod Organizer 2's interface should open.
- If prompted, choose a Portable installation, not a Global one. This is the only supported installation type for MO2-LINT.
- Under **Executables**, the game should be listed.
- Try installing a mod, or clicking Nexus Mods' "Mod Manager Download" button, to confirm the NXM handler works (if you have a Nexus Premium account).

{: .tip }
> If something looks wrong at this stage, check [Troubleshooting](../troubleshooting/) before opening an issue. Most first-run problems are covered there.

## 5. Post-Installation

You're set up. From here:

- [CLI Guide](../guide/) for every command and option.
- [Game Guides](../game-guides/) for any game-specific quirks.
