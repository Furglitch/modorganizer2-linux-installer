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

On ARM64 Linux, including Steam Frame, use `mo2-lint-aarch64`. MO2-LINT installs [MO2 2.5.2-woa.1](https://github.com/ndabas/modorganizer/releases/tag/v2.5.2-woa.1), which includes the USVFS fix needed to launch games on ARM64.

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
| **Proton 11.0** | The main version of Proton that MO2-LINT is tested against. Early versions may work but aren't guaranteed to, and are not supported. |
| **GE-Proton11** | An alternate, community maintained version of Proton, which may provide game compatibility and bugfixes that standard Proton does not. More information can be found on their [GitHub repo](https://github.com/gloriouseggroll/proton-ge-custom). |
| **Proton 10.0-4** | There are known issues with Mod Organizer 2 on this version, such as [#878](https://github.com/Furglitch/modorganizer2-linux-installer/issues/878) |
| **Proton 9.0-4** | Known to be incapable of launching some games, such as Fallout 4. |

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
