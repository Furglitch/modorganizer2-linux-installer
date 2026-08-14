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

## Preserving save data across a prefix reset

Deleting and recreating a game's prefix loses your saves unless backed up first. Save data lives inside the prefix under the `users` folder:

- **Steam**: `<prefix>/pfx/drive_c/users/`
- **GOG / Epic (Heroic)**: `<prefix>/drive_c/users/`

**To preserve your saves:**

1. Copy the `users` folder somewhere safe before deleting the prefix:
   ```bash
   cp -r /path/to/prefix/drive_c/users ~/.tmp/mo2-lint/users-backup
   ```
2. Delete the old prefix and launch the game once to generate a fresh one, then exit.
3. Restore your saves:
   ```bash
   cp -r ~/.tmp/mo2-lint/users-backup/. /path/to/new/prefix/drive_c/users/
   ```

{: .note }
> Overwriting the whole `users` folder should be safe for save data, but some per-user configuration inside the prefix (e.g. registry hives under `users/<name>/`) may carry over stale settings from the old prefix.

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
