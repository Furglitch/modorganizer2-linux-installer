---
title: Launch & Proton Issues
layout: default
nav_order: 2
parent: Troubleshooting
---

# Launch & Proton Issues

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Check launch options

If you add anything to your Steam launch arguments, make sure `%command%` is included **exactly once**:

```
%command%
```

Variables go before it, flags go after:

```
VARIABLE=value VARIABLE2=value %command% --flag
```

{: .danger }
> Adding `%command%` more than once **will** cause problems.

## Flatpak Steam issues

If Steam is installed via Flatpak, MO2 may not have access to necessary files. Grant it access to your home directory:

```bash
flatpak override --user --filesystem=home com.valvesoftware.Steam
```

If the MO2 instance lives outside `$HOME`, replace `home` with the appropriate path, e.g. `--filesystem=/path/to/directory`.

## GameMode interference

`gamemoderun` typically improves Proton game performance, but it **will** cause MO2 to fail to launch. Remove it from the launch options.

## Directories outside home

If MO2 or your game is installed outside your home directory, add the path to `STEAM_COMPAT_MOUNTS`:

```bash
STEAM_COMPAT_MOUNTS="/path/to/directory" %command%
```

Separate multiple directories with colons:

```bash
STEAM_COMPAT_MOUNTS="/path/to/dir1:/path/to/dir2" %command%
```

## Wrong Proton version

MO2-LINT currently only supports Proton 11.0.

- **Steam**: Properties → Compatibility → Force use of specific Steam Play compatibility tool → Proton 11.0
- **Heroic**: Settings → Wine → Wine Version → Proton - Proton 11.0

See [Setting up Proton](../getting-started/proton-setup) for full steps.

## Prefix not initialized

Launch the game at least once through Steam/Heroic **before** installing MO2-LINT, so the launcher can set up the Proton prefix with its default dependencies.
