---
title: Creating an Instance
layout: default
nav_order: 1
parent: TUI Guide
---

# Creating an Instance

Choose **Create New Instance** from the main menu. This is the TUI version of the [`install`](../guide/install) command.

{: .warning }
> Launch the game through Steam or Heroic at least once before you start, as described in [First Launch](../getting-started/first-launch#1-launch-the-game-once-if-you-havent-already). MO2-LINT needs the Proton prefix that this creates.

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## 1. Choose a launcher and game

![The New Instance screen, with Steam and New Vegas selected]({{ '/assets/images/tui/new-instance-game.png' | relative_url }})

**Launcher**
: The launcher you own the game on: Steam, GOG, or Epic Games. If you've set a [Primary Launcher](./settings), it's highlighted for you. The game list only shows games available on the highlighted launcher.

**Game**
: The game to set up. If you switch launchers, your game stays selected as long as the new launcher has it.

Press **Next** to continue.

## 2. Configure the instance

![The New Instance Settings screen]({{ '/assets/images/tui/new-instance-config.png' | relative_url }})

**Script Extender**
: Install the game's script extender (SKSE, F4SE, NVSE, etc.). Only shown for games that have one. If more than one version is available, you'll be asked to pick one during the install.

**Plugins**
: MO2 plugins to install. Toggle each one with <kbd>Space</kbd>. Plugins from your [Primary MO2 Plugins](./settings) setting start ticked.

**Themes**
: An MO2 theme to apply, or **None**. Starts on your [Primary MO2 Theme](./settings). See [Themes](../guide/themes) for what each option does.

**Install Directory**
: Where to create the instance. The placeholder shows the folder MO2-LINT uses if you leave this empty, built from your [Default Instance Folder and Instance Folder Name](./settings) settings. If no default folder is set, you must enter a path here. `~` is expanded to your home folder.

  If the directory already exists, it must be empty.

Press **Next** to continue.

## 3. Confirm your prefix setup

MO2-LINT shows the steps to prepare your game's Proton prefix for the launcher you picked. For Steam, this includes forcing the game to use the custom **MO2** compatibility tool.

![The prefix setup dialog for a Steam game]({{ '/assets/images/tui/new-instance-prefix.png' | relative_url }})

| Button | Result |
|:--|:--|
| **Yes** | Starts the install. |
| **No, continue anyway** | Starts the install without confirming the steps. MO2-LINT may warn you or stop if the prefix isn't ready. |
| **Cancel** | Returns to the configuration screen. |

## 4. Install

The [progress dialog](./#progress-prompts-and-messages) shows the install as it runs. When it finishes, press **Close**:

- **If it completed**, you're taken back to the main menu, and the instance count goes up by one.
- **If it didn't complete**, you stay on the configuration screen, so you can adjust your choices and try again. Check the log in the dialog, and [Installation Issues](../troubleshooting/installation-issues), for the cause.

The log also contains the launch instructions for your new instance. Continue from step 3 of [First Launch](../getting-started/first-launch#3-launch-through-steam-or-heroic) to start MO2 for the first time.
