---
title: Fallout 3
layout: default
nav_order: 2
parent: Game-Specific Instructions
---

# Fallout 3

Fallout 3 GOTY released an anniversary update in 2024, but it appears the majority of the modding community have decided to stick with the 2021 release, or just have yet to upgrade.

The recommended method of downgrading is with the Fallout Anniversary Patcher, with instructions and links provided below.

### Using the Fallout Anniversary Patcher

1. Install a clean copy of _Fallout 3 GOTY_
2. Download the '[Fallout Anniversary Patcher](https://www.nexusmods.com/fallout3/mods/24913)'. Extract the .7z file into the game folder ("Fallout 3 goty")
3. In terminal, run the below command. Make sure you replace `/path/to` to the path of your Steam library.
   ```bash
   protontricks-launch "/path/to/Fallout 3 goty/Patcher.exe"
   ```
4. When the ProtonTricks GUI appears, choose "Fallout 3 - Game of the Year Edition: 22370"
5. Check the terminal for output of the following lines
   ```bash
   Hash checks completed. Found Steam/GOG executable.
   Backup created.
   xdelta3: secondary compression: lzma
   xdelta3: source <path>\Fallout 3 goty\Fallout3_backup.exe source size 16.1 MiB [16855040] blksize 64.0 MiB window 64.0 MiB
   xdelta3: 0: in 3.63 MiB: out 8.00 MiB: total in 3.63 MiB: out 8.00 MiB: 198 ms
   xdelta3: 1: in 1.97 MiB: out 6.34 MiB: total in 5.60 MiB: out 14.3 MiB: 93 ms
   xdelta3: finished in 297 ms; input 5874097 output 15038976 bytes (256.02%)
   Patching completed successfully.
   ```
6. Once patching is confirmed successful, run the MO2 installer.
