---
title: Setting up Proton
layout: default
nav_order: 3
parent: Getting Started
---

# Setting up Proton

Proton is required for MO2-LINT to function. MO2-LINT is tested against **Proton 11.0 only**; older versions may work but aren't supported.

These same steps are also shown during the interactive install process.

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Steam

In order to install the custom compatibility tool, **Proton 11.0** is required to be installed, as listed in the [Compatibility Layer](./requirements#supported-versions) requirements.

After installation, you will need to set your game to use the custom compatibility tool created by the installer, as detailed by the [First Launch guide](./first-launch#steam)

## Heroic Games Launcher (GOG and Epic)

{: .note }
> If Proton doesn't appear in the Wine Version dropdowns, make sure it is installed via Steam and enable **Allow using Valve Proton builds to run games** under Heroic's **Advanced** settings.

{: .tip }
> Under **Game Defaults** → **Other**, enabling **Use Steam Runtime** is recommended and may improve compatibility.

### Option A: Universal Setting

1. In Heroic, go to **Settings** → **Game Defaults**.
2. In the **Wine Version** dropdown, select **Proton 11.0**.

### Option B: Per-Game Setting

1. Right-click the game in your Heroic library → **Settings** → **Wine** tab.
2. In the **Wine Version** dropdown, select **Proton 11.0**.

## Post-Setup

{: .warning }
> After setting up Proton, **launch the game at least once**. This lets Steam create the Proton prefix with its default dependencies, which are not bundled with MO2-LINT.

---

Continue to [First Launch](./first-launch) to verify everything is wired up correctly.
