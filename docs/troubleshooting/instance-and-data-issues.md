---
title: Instance & Data Issues
layout: default
nav_order: 4
parent: Troubleshooting
---

# Instance & Data Issues

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Instance not found

If `mo2-lint list` doesn't show your instance, the state file may be out of date. It's located at:

```
~/.config/mo2-lint/state.json
```

{: .danger }
> Do not manually edit this file. If it becomes corrupted, you may need to reinstall MO2-LINT instances.

## Cannot update a pinned instance

Pinned instances won't update their MO2 version. Unpin first:

```bash
mo2-lint unpin /path/to/instance
```

See [Managing Instances](../guide/managing-instances#pin) for more on pinning.

## Refreshing a Prefix

A Wine/Proton prefix contains the filesystem of the simulated Windows environment that Wine/Proton uses to run your game. Depending on changes made to the prefix, it may be beneficial to reset the prefix.

Prefix folders can be found in the below locations. If you installed a game in a secondary location (second drive, etc), the game's prefix will be near that same location.
- **Steam**: `<Steam Library location>/steamapps/compatdata/<Game ID>/`
- **Heroic (GOG / Epic)**: `<Heroic Library location>/prefixes/<Game Name>/`

{: .warning }
> If you have save data, see **Preserving save data across a Prefix reset** below *before* proceeding with resetting your game's prefix.

After preserving saves where necessary, delete the prefix folder and launch the game once to allow standard setup to process. For games with a launcher, allowing the launcher to appear should be enough. For games without a launcher, wait until the main menu appear before closing.

### Preserving save data across a Prefix reset

Deleting and recreating a game's prefix loses your saves unless backed up first. Save data lives inside the prefix under the `users` folder:

**To preserve your saves:**

1. Copy the `users` folder somewhere safe before deleting the prefix:
   ```bash
   cp -r </path/to/prefix>/pfx/drive_c/users ~/.tmp/mo2-lint/users-backup # For Steam
   cp -r </path/to/prefix>/drive_c/users ~/.tmp/mo2-lint/users-backup # For Heroic
   ```
2. Delete the old prefix and launch the game once to generate a fresh one, then exit.
3. Restore your saves:
   ```bash
   cp -r ~/.tmp/mo2-lint/users-backup/. </path/to/new/prefix/users/folder>
   ```

{: .note }
> Overwriting the whole `users` folder should be safe for save data, but some per-user configuration inside the prefix (e.g. registry hives under `users/<name>/`, altered game configuration files) may carry over stale settings from the old prefix.

## Log files

Installation and error logs are stored at:

```
~/.cache/mo2-lint/logs/
```

Include these when reporting issues.

## Reporting issues

If your issue isn't covered anywhere in Troubleshooting:

1. Check [GitHub Issues](https://github.com/furglitch/modorganizer2-linux-installer/issues) to see if it's already reported.
2. If not, open a new issue with as much detail as possible. Include logs and, if applicable, screenshots.
