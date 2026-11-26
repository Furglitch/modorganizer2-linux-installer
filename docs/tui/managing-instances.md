---
title: Managing Instances
layout: default
nav_order: 2
parent: TUI Guide
---

# Managing Instances

Choose **Manage Instances** from the main menu to update, pin, or uninstall your instances. This covers the [`update`](../guide/update), [`list`, `pin`, `unpin`, and `uninstall`](../guide/managing-instances) commands.

The menu item is disabled until you've created at least one instance.

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

![The Manage Instances screen, with a New Vegas instance selected]({{ '/assets/images/tui/manage-instances.png' | relative_url }})

## Instance details

Highlight an instance on the left to see its details in the middle column:

| Field | Meaning |
|:--|:--|
| **Game** | The game identifier, as used by the CLI. |
| **MO2 Path** | Where the MO2 instance is installed. |
| **Game Path** | Where the game itself is installed. |
| **Pinned** | Whether the instance is [pinned](#pin-and-unpin). |
| **Launcher** | `steam`, `gog`, or `epic`. |
| **Script Extender** | The installed script extender version, or `None`. |
| **Plugins** | The MO2 plugins installed with the instance. |

The buttons on the right act on the highlighted instance.

## Update

Downloads the current MO2 build for the instance and refreshes its launch configuration, in a [progress dialog](./#progress-prompts-and-messages). See [`update`](../guide/update) for what this changes.

Pinned instances can't be updated. Unpin the instance first.

## Pin and Unpin

Pinning locks an instance at its current MO2 version, so **Update** skips it. The button label switches between **Pin** and **Unpin** to match the highlighted instance. The change applies straight away.

## Uninstall

1. Press **Uninstall**, then **Uninstall** again to confirm.
2. If the instance folder still exists, choose what happens to its files:
   - **Move to Trash**: the folder goes to your desktop's trash, so you can still restore it.
   - **Delete Permanently**: asks for one more confirmation, then deletes the folder.
   - **Cancel**: stops without uninstalling.
3. The uninstall runs in a progress dialog. When you close it, the instance is removed from the list.

If the instance folder is already gone, step 2 is skipped. MO2-LINT removes what it left in the game folder (such as its links and any script extender files it installed) and stops tracking the instance.

{: .warning }
> At the final **Delete Permanently** confirmation, pressing **Cancel** doesn't stop the uninstall. It moves the files to the trash instead. Use **Cancel** at step 1 or 2 if you want to keep the instance.
