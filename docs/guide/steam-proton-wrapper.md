---
title: Steam Proton wrapper
layout: default
nav_order: 2
parent: Guide
---

# Steam Proton wrapper

{: .note }
> This page is mainly for users who are interested in the technical details of how the Steam Proton wrapper works. For most users, this is not required reading. If you just want to install Mod Organizer 2 for a Steam game, see the [install](./install) reference.

This installer provides a custom Steam compatibility tool (a thin Proton wrapper) that intercepts the game's normal executable and launches Mod Organizer 2 instead. The wrapper is installed per-Steam appid into Steam's `compatibilitytools.d` directory and is selectable from the game's **Properties → Compatibility** tab.

**Key facts**

- **Tool ID**: `mo2_<appid>_redirector` (installed to `compatibilitytools.d/mo2_<appid>_redirector`)
- **Marker file**: `.mo2-lint-proton-wrapper` inside the installed tool folder
- **Default Proton version**: Proton 11.0 (overrideable with `--proton-version` during `mo2-lint install`)

## How it works

The wrapper drops a small script and metadata into a compatibility tool directory that Steam recognizes. When selected for a game, Steam launches the wrapper which in turn runs the real Proton runtime but replaces the game's executable with `mo2-redirector.exe` so Mod Organizer 2 is started instead of the game.

## What the installer does

When you run `mo2-lint install` for a Steam game the installer will:

- Resolve a Proton runtime directory (default: `Proton 11.0`).
- Render the bundled wrapper template and write it to `~/.local/share/Steam/compatibilitytools.d/mo2_<appid>_redirector`.
- Add the redirector's metadata so Steam shows the tool in the compatibility dropdown.
- Restart Steam automatically (or ask you to) so the change is picked up.

If you passed `--proton-version` to `mo2-lint install` that value is used instead of the default.

## Post-install

To set the wrapper for your game, follow these steps:

1. Open your Steam Library and right‑click the game.
2. Choose **Properties** → **Compatibility**.
3. Enable **Force the use of a specific Steam Play compatibility tool**.
4. From the dropdown, select the Proton version created by this installer — it will be listed as `MO2 <game>` (for example: `MO2 Fallout 4`).

Important: keep at least one other game set to the original Proton version (the one you replaced) so Steam doesn't consider it unused and automatically remove it. A non‑Steam game entry works for this purpose.

## protontricks and PROTON_VERSION

Some tools (notably `protontricks`) expect a full Proton runtime inside the compatibility tool. The wrapper we install intentionally contains only the files needed to redirect the launch. To avoid failures when `protontricks` runs against a game using the wrapper, `mo2-lint` sets the `PROTON_VERSION` environment variable when invoking `protontricks` so it resolves the real Proton runtime instead of the wrapper.

If you run `protontricks` yourself outside of `mo2-lint`, set `PROTON_VERSION` to the same Proton version used by the wrapper (for example `Proton 11.0`) before invoking protontricks.

## Reverting / Uninstalling

- To remove the wrapper and restore the previous behaviour, either use `mo2-lint uninstall` for the instance you created or remove the compatibility tool directory `~/.local/share/Steam/compatibilitytools.d/mo2_<appid>_redirector` manually and restart Steam.
- If Steam removes the original Proton runtime while you were using the wrapper, reinstall the original Proton runtime from Steam and reassign it to at least one game to prevent automatic cleanup.

## Troubleshooting

- If the game still launches directly instead of Mod Organizer 2, confirm you selected the MO2 compatibility tool in the game's Compatibility dropdown and restart Steam.
- If `protontricks` fails, set `PROTON_VERSION` to the wrapper's underlying Proton runtime (see the `mo2-lint` output after installation for the exact version name) and try again.

---

For general first-run instructions see the [First Launch](../getting-started/first-launch) guide and the [install](./install) reference.
