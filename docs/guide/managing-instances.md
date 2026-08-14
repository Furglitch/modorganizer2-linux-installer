---
title: Managing Instances
layout: default
nav_order: 3
parent: CLI Guide
---

# Managing Instances

Reference for `uninstall`, `list`, `pin`, and `unpin`. Everything besides creating (`install`) or refreshing (`update`) an instance.

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## `list`

Lists all MO2 instances currently tracked by MO2-LINT.

```bash
mo2-lint list [options]
```

| Option | Description |
|:--|:--|
| `--game <game>`, `-g <game>` | Filter to instances for the specified game. |
| `--directory <directory>`, `-d <directory>` | Filter to instances at or within the specified directory. |

## `uninstall`

Removes an existing instance, unregisters the launch option, and removes it from the state file. Without options, lists all instances and lets you pick one or more to remove.

```bash
mo2-lint uninstall [options]
```

| Option | Description |
|:--|:--|
| `--game <game>`, `-g <game>` | Filter to instances for the specified game. |
| `--directory <directory>`, `-d <directory>` | Filter to instances at or within the specified directory. |

## `pin`

Prevents an instance's MO2 version from being changed by [`update`](./update.html). Useful when a newer MO2 version breaks compatibility with specific mods or plugins.

```bash
mo2-lint pin <directory>
```

`<directory>` is required and must be the exact instance path, parent directories aren't accepted.

## `unpin`

Reverses `pin`, allowing `update` to change the MO2 version again.

```bash
mo2-lint unpin <directory>
```

`<directory>` is required and must be the exact instance path.
