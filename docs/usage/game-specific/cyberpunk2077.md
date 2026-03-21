---
title: Cyberpunk 2077
layout: default
nav_order: 1
parent: Game-Specific Instructions
---

# Cyberpunk 2077

Some mods and scripts for Cyberpunk 2077 will fail to load or function properly without including the `winmm` and `version` libraries in `WINEDLLOVERRIDES`. If you are experiencing issues with mods or scripts not working, try adding the following to your launch options:

```bash
WINEDLLOVERRIDES="winmm,version=n,b" %command%
```
