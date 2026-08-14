---
title: Cyberpunk 2077
layout: default
nav_order: 1
parent: Game Guides
---

# Cyberpunk 2077

{: .warning }
> Some mods and scripts for Cyberpunk 2077 fail to load or function properly without the `winmm` and `version` libraries in `WINEDLLOVERRIDES`.

If you're experiencing issues with mods or scripts not working, add the following to your Steam launch options:

```bash
WINEDLLOVERRIDES="winmm,version=n,b" %command%
```
