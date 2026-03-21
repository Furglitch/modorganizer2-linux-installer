---
title: Fallout London
layout: default
nav_order: 3
parent: Game-Specific Instructions
---

# Fallout London

Fallout London's installation process is a bit different from other games, as it is a mod for Fallout 4 that's only available via GOG.

MO2-LINT only provides support for the One-Click Edition of Fallout London, which is available for free on GOG and can be claimed [here](https://www.gog.com/en/game/fallout_london_oneclick_edition).

After claiming, installing, and launching the game at least once, you can set up an MO2 instance for it by using the `falloutlondon` game identifier.

### Additional Notes

- Fallout London includes its own copy of F4SE. As such, F4SE is not installable via MO2-LINT.
  Ensure you are launching the game from MO2 with the included F4SE executable selected, and not the default Fallout 4 executable, to ensure that the game runs properly.

- Nexus' "Mod Manager Download" button does not work with Fallout London instances, whether the mod is for Fallout 4 or Fallout London.
  - For Fallout 4 mods, this is because the NXM:// handler is searching for Fallout 4 instances and does not recognize Fallout London instances.
  - For Fallout London mods, this is a limitation of Mod Organizer itself as it recognizes the Fallout London instance as a Fallout 4 instance. This is not something that can be fixed on the MO2-LINT side.
  - In either case, you can still download and install mods manually from Nexus.

- If you wish to install the non-'One-Click' version of Fallout London (i.e. installing for a different launcher), keeping in mind that it is ***not supported*** by MO2-LINT, you can follow the instructions in [this previous commit](https://github.com/Furglitch/modorganizer2-linux-installer/commit/4642d0d4ffec657d2c9447805cf7cc88f467221e#diff-fd60fe3a218a9c9a679a56bc67ee843e215fdea22bfcefb535305dba5bb213a1), using the `fallout4` identifier instead of the `falloutlondon` identifier. Note that these instructions are outdated and may not work with the current versions of MO2-LINT, Fallout 4, or Fallout London.
