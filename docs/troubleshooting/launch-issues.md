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

If Steam or Heroic is installed via Flatpak, MO2-LINT applies filesystem overrides during install so the sandbox can see the instance directory, the redirector in the game folder, and `~/.config/mo2-lint`.

If you need to apply the override manually, grant the launcher access to the relevant paths:

```bash
flatpak override --user --filesystem=/path/to/instance --filesystem=/path/to/game --filesystem=~/.config/mo2-lint com.valvesoftware.Steam
flatpak override --user --filesystem=/path/to/instance --filesystem=/path/to/game --filesystem=~/.config/mo2-lint com.heroicgameslauncher.hgl
```

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

## 'Could not start <flag>' errors

Mod Organizer 2 attempts to filter out launch flags, as they are known to be interpreted as an executable.

If you see an error like `Could not start -silent-crashes` or `Could not start --vr`, please report it on the [GitHub Issues](https://github.com/furglitch/modorganizer2-linux-installer/issues) page. We will add the flag to the list of known launch arguments and update the redirector.
