---
title: TUI Guide
layout: default
nav_order: 3
has_children: true
description: "Using MO2-LINT's interactive terminal interface."
---

# TUI Guide

MO2-LINT includes a full-screen terminal interface (TUI) that covers the same tasks as the [CLI](../guide/): creating instances, updating, pinning and uninstalling them, and editing your settings. You don't need to remember any commands or flags.

{: .note }
> Read through [Game Guides](../game-guides/) for your game before creating an instance. Some games need extra steps.

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Opening the TUI

Run MO2-LINT without a command:

```bash
mo2-lint
```

Any command (`install`, `update`, `list`, ...) runs the CLI instead, as described in the [CLI Guide](../guide/).

{: .warning }
> The TUI needs a terminal of at least **120 × 30** characters. If your window is smaller, MO2-LINT shows a notice with the current size until you resize it.

## The main menu

![The MO2-LINT main menu, with Create New Instance highlighted]({{ '/assets/images/tui/main-menu.png' | relative_url }})

| Menu item | What it does |
|:--|:--|
| **Create New Instance** | Set up Mod Organizer 2 for a game. See [Creating an Instance](./new-instance). |
| **Manage Instances** | Update, pin, or uninstall existing instances. See [Managing Instances](./managing-instances). Disabled until you have at least one instance. |
| **Settings** | Edit your default options. See [Settings](./settings). |
| **Documentation** | Opens this documentation site in your browser. |
| **Exit** | Closes MO2-LINT. |

The counter below the menu shows how many instances MO2-LINT is tracking.

## Getting around

The TUI works with the keyboard or the mouse. The footer at the bottom of each screen lists the shortcuts available there.

| Key | Action |
|:--|:--|
| <kbd>↑</kbd> / <kbd>↓</kbd> | Move through a list. |
| <kbd>Tab</kbd> / <kbd>Shift</kbd>+<kbd>Tab</kbd> | Move between lists, fields, and buttons. |
| <kbd>Enter</kbd> | Select the highlighted item or press the focused button. |
| <kbd>Space</kbd> | Toggle a checkbox, or a plugin in a plugin list. |
| <kbd>Esc</kbd> | Go back one screen, or cancel a dialog. |
| <kbd>T</kbd> | Switch between the dark and light colour themes. |
| <kbd>Ctrl</kbd>+<kbd>P</kbd> | Open the command palette. |
| <kbd>Ctrl</kbd>+<kbd>S</kbd> | Save settings (Settings screen only). |

## Progress, prompts, and messages

Installing, updating, and uninstalling open a progress dialog. It shows the current step and the live log at the level set in [Settings](./settings).

![The progress dialog while an install is running]({{ '/assets/images/tui/progress-running.png' | relative_url }})

When the task ends, the status line reads **Completed.** or **Did not complete. See the log above.** Press **Close** to continue. The button turns green on success and red on failure.

![The progress dialog after a successful install]({{ '/assets/images/tui/progress-complete.png' | relative_url }})

If MO2-LINT needs you to choose something while it works (a launcher, or a script extender version, for example), a selection dialog pops up. Pick an option and press **Select**, or **Cancel** to stop.

Warnings and errors that happen outside a progress dialog appear as notifications in the bottom-right corner.

{: .tip }
> Full logs are always written to disk at `TRACE` level, whatever the on-screen log level is. Include them when reporting an issue; see [Troubleshooting](../troubleshooting/).
