---
title: Fallout London
layout: default
nav_order: 4
parent: Game Guides
---

# Fallout London

Fallout London's installation process differs from other games, as it's a mod for Fallout 4 that's only available via GOG.

{: .note }
> MO2-LINT only supports the **One-Click Edition** of Fallout London, free on GOG. Claim it [here](https://www.gog.com/en/game/fallout_london_oneclick_edition).

After claiming, installing, and launching the game at least once, set up an instance using the `falloutlondon` game identifier.

## Additional notes

- Fallout London bundles its own copy of F4SE, so F4SE is **not** installable via MO2-LINT. Launch the game from MO2 with the included F4SE executable selected, not the default Fallout 4 executable.
- Nexus' "Mod Manager Download" button does **not** work with Fallout London instances, for either Fallout 4 or Fallout London mods:
  - **Fallout 4 mods**: the NXM handler searches for Fallout 4 instances and doesn't recognize Fallout London instances.
  - **Fallout London mods**: a limitation of Mod Organizer itself, which recognizes the instance as Fallout 4. Not fixable on the MO2-LINT side.
  - Either way, you can still download and install mods manually from Nexus.

{: .unsupported }
> Want the non-"One-Click" version (a different launcher)? It's not supported by MO2-LINT, but see [this previous commit](https://github.com/Furglitch/modorganizer2-linux-installer/blob/4642d0d4ffec657d2c9447805cf7cc88f467221e/docs/installation-and-usage/usage/game-specific/folon.md) for the old approach using the `fallout4` identifier instead of `falloutlondon`. These instructions are outdated and may not work with current versions of MO2-LINT, Fallout 4, or Fallout London.
