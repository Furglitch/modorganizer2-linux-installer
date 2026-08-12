---
title: Themes
layout: default
nav_order: 3
parent: Usage
---

# Themes

The use of the `--theme` option is supported in MO2-LINT for the `install` and `update` commands. This allows you to specify a theme to be applied to the Mod Organizer 2 instance during installation or update.

> NOTE: When you launch Mod Organizer 2 for the first time, you may receive a warning stating `Cannot open instance 'Portable', the managed game was not found in the INI file`. This is expected behavior and can be ignored. It occurs because the theme is applied before the game path is set in the configuration file.

## Available Themes

| Theme Name | Slug | Availability | Preview |
|------------|------|---------|---------|
| 1809 Dark Mode | 1809 | Included in MO2 | ![1809 Dark Mode](https://staticdelivery.nexusmods.com/mods/1704/images/24006/24006-1587914446-1164006035.png) |
| Dark | dark | Included in MO2 | Unavailable |
| Dracula | dracula | Included in MO2 | Unavailable |
| Night Eyes | night-eyes | Included in MO2 | Unavailable |
| Paper Automata | paper-automata | Included in MO2 | ![Paper Automata](https://staticdelivery.nexusmods.com/mods/110/images/64439/64439-1624777223-1765497352.png) |
| Paper Black Mono | paper-mono-black | Included in MO2 | ![Paper Black Mono](https://staticdelivery.nexusmods.com/mods/110/images/64439/64439-1624777245-537407380.png) |
| Paper Dark | paper-dark | Included in MO2 | ![Paper Dark](https://staticdelivery.nexusmods.com/mods/110/images/64439/64439-1624777184-129358388.png) |
| Paper Light | paper-light | Included in MO2 | ![Paper Light](https://staticdelivery.nexusmods.com/mods/110/images/64439/64439-1624777203-1758304706.png) |
| Paper White Mono | paper-mono-white | Included in MO2 | ![Paper White Mono](https://staticdelivery.nexusmods.com/mods/110/images/64439/64439-1624777244-1568414922.png) |
| Parchment | parchment | Included in MO2 | Unavailable |
| Skyrim | skyrim | Included in MO2 | ![Skyrim](https://staticdelivery.nexusmods.com/mods/110/images/73817-0-1456426673.png) |
| Transparent Style (Fallout 3) | transparent-fo3 | Included in MO2 | Unavailable |
| Transparent Style (Fallout 4) | transparent-fo4 | Included in MO2 | Unavailable |
| Transparent Style (Morrowind) | transparent-morrowind | Included in MO2 | Unavailable |
| Transparent Style (Skyrim) | transparent-skyrim | Included in MO2 | Unavailable |
| Transparent Style (Starfield) | transparent-starfield | Included in MO2 | Unavailable |
| VS15 | vs15 | Included in MO2 | ![VS15](https://staticdelivery.nexusmods.com/mods/110/images/73273-1-1454953359.png) |
| VS15 (Green) | vs15-green | Included in MO2 | ![VS15 Colored](https://staticdelivery.nexusmods.com/mods/110/images/73273-0-1455370808.png) |
| VS15 (Orange) | vs15-orange | Included in MO2 | See VS15 (Green) |
| VS15 (Pink) | vs15-pink | Included in MO2 | See VS15 (Green) |
| VS15 (Purple) | vs15-purple | Included in MO2 | See VS15 (Green) |
| VS15 (Red) | vs15-red | Included in MO2 | See VS15 (Green) |
| VS15 (Yellow) | vs15-yellow | Included in MO2 | See VS15 (Green) |
| Fluency Dark | fluency-dark | Nexus Download | ![Fluency Dark](https://staticdelivery.nexusmods.com/mods/1704/images/71449/71449-1657907412-1078074728.png) |
| Fluency Midnight | fluency-midnight | Nexus Download | ![Fluency Midnight](https://staticdelivery.nexusmods.com/mods/1704/images/71449/71449-1657907407-622499738.png) |
| Fluency White | fluency-white | Nexus Download | ![Fluency White](https://staticdelivery.nexusmods.com/mods/1704/images/71449/71449-1657907402-335655203.png) |
| Catppuccin Latte | catppuccin-latte | Nexus Download | ![Catppuccin Latte](https://staticdelivery.nexusmods.com/mods/2295/images/2068/2068-1783097951-126309914.png) |
| Catppuccin Mocha | catppuccin-mocha | Nexus Download | ![Catppuccin Mocha](https://staticdelivery.nexusmods.com/mods/2295/images/2068/2068-1783097947-1098656301.png) |

For example, to install Mod Organizer 2 with the Fluency Dark theme, you would use the following command:

```bash
mo2-lint install -t fluency-dark
```

## Desktop Environment Themes

Using `--theme auto` will also create a theme based on your current desktop environment's color scheme. This allows for a more integrated look and feel with your operating system.

This feature currently works with KDE and GTK desktop environments by pulling from the ~/.config/kdeglobals or ~/.config/gtk-3.0/colors.css files, respectively.
