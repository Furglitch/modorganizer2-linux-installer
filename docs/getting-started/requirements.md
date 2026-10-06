---
title: Requirements
layout: default
nav_order: 1
parent: Getting Started
---

# Requirements

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Operating System

{: .danger }
> **Linux only.** MO2-LINT does not work on Windows, MacOS, or any other operating system.

### ARM64 support status

MO2-LINT can run natively on ARM64 Linux, including Steam Frame. The ARM64 binary is named `mo2-lint-aarch64`.

{: .warning }
> Mod Organizer 2 cannot launch games or tools on ARM64 with its bundled USVFS. MO2 requires the [USVFS ARM64 patch](https://github.com/ModOrganizer2/usvfs/pull/93). You can download patched USVFS binaries from the [releases linked in that PR](https://github.com/ndabas/modorganizer/releases) and apply them to an existing MO2 installation without waiting for an official MO2 release containing the fix. MO2-LINT does not apply that patch. Steam Frame installation instructions are deferred until MO2 includes the fix.

## Launchers

You need at least one of:

- Steam - for Steam games
- Heroic Games Launcher - for GOG and Epic Games Store games

{: .unsupported }
> MO2-LINT does not support Lutris or any other game launchers.

## Compatibility Layer

See [Setting up Proton](./proton-setup).

### Supported Versions

| Layer | Notes |
|:--|:--|
| **Proton 11.0** | The only officially tested and supported version. Early versions may work but aren't guaranteed to, and are not supported. |
| **Proton 10.0-4** | There are known issues with Mod Organizer 2 on this version, such as [#878](https://github.com/Furglitch/modorganizer2-linux-installer/issues/878) |
| **Proton 9.0-4** | Known to be incapable of launching games such as Fallout 4. |

## System Packages

| Package | Why it's needed | Distro Inclusion | Required? |
|:--|:--|:--|:--|
| xdg-mime | Sends Nexus Mods downloads to MO2 via the `nxm://` handler. Allows MO2 to use your default applications for folders and various file types. | Included by default on many distros. | Required |
| procps | Provides `pgrep`, used to auto-restart Steam/Heroic while adding launch options. | Included by default on many distros. Fedora known not to. | Required |
| cabextract | Used by *winetricks* to extract fonts and DirectX components (`arial`, `d3dcompiler_43`, `d3dx9`, `xact`, etc.). | Most distros don't include this by default. MO2-LINT downloads it if it isn't installed. | Optional |
| 7z | Extracts the Mod Organizer 2 archive and some *winetricks* downloads. | Not included on every distro. MO2-LINT downloads it if it isn't installed. | Optional |
| protontricks | Manages the Proton prefix and installs MO2 dependencies. | Bundled with MO2-LINT. | Optional |
| winetricks | Used to manage Heroic prefixes and other Wine-related tasks. | Bundled with MO2-LINT, but falls back to the system version if installed. | Optional |

---

Once these are in place, continue to [Installing MO2-LINT](./installing).
