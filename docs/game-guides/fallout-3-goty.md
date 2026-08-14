---
title: Fallout 3
layout: default
nav_order: 2
parent: Game Guides
---

# Fallout 3

Fallout 3 GOTY received an anniversary update in 2024, but most of the modding community has stuck with the 2021 release, or hasn't upgraded their mods. The recommended fix is downgrading with the Fallout Anniversary Patcher.

## Downgrading with the Fallout Anniversary Patcher

1. Install a clean copy of **Fallout 3 GOTY**.
2. Download the [Fallout Anniversary Patcher](https://www.nexusmods.com/fallout3/mods/24913) and extract the `.7z` into the game folder (`Fallout 3 goty`).
3. In a terminal, run (replacing `/path/to` with your Steam library path):
   ```bash
   protontricks-launch "/path/to/Fallout 3 goty/Patcher.exe"
   ```
4. When the Protontricks GUI appears, choose **Fallout 3 - Game of the Year Edition: 22370**.
5. Confirm the terminal output looks like this:
   ```
   Hash checks completed. Found Steam/GOG executable.
   Backup created.
   xdelta3: secondary compression: lzma
   xdelta3: source <path>\Fallout 3 goty\Fallout3_backup.exe source size 16.1 MiB [16855040] blksize 64.0 MiB window 64.0 MiB
   xdelta3: 0: in 3.63 MiB: out 8.00 MiB: total in 3.63 MiB: out 8.00 MiB: 198 ms
   xdelta3: 1: in 1.97 MiB: out 6.34 MiB: total in 5.60 MiB: out 14.3 MiB: 93 ms
   xdelta3: finished in 297 ms; input 5874097 output 15038976 bytes (256.02%)
   Patching completed successfully.
   ```

{: .tip }
> Once patching is confirmed successful, run the [`install`](../guide/install) command as normal.
