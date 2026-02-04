---
title: Configuration Files
layout: default
nav_order: 1
parent: Contributing
---

# Configuration Files

MO2-LINT uses YAML configuration files to define various resources for the installer, such as supported games. These configuration files are located in the [`configs/`] directory of the project.

## `games_info.yml`

The `games_info.yml` file contains information about the supported games, including their names, executable paths, and any specific configurations required for installation. The structure of the file is as follows:

```yaml
schema:

games:
  <game_id>:
    display_name: <display_name>
    nexus_slug: <nexus_slug>
    launcher:
      steam: <steam>
      gog: <gog>
      epic: <epic>
    subdirectory: <subdirectory>
    executable: <executable>
    tricks:
      - <trick_1>
      - <trick_2>
    script_extenders: # Further details below
    workarounds: # Further details below
```

**Key Fields:**
- `game_id`: A unique identifier for the game. This is used in the `<game>` argument of the installer commands.
- `display_name`: The human-readable name of the game.
- `nexus_slug`: The Nexus Mods slug for the game, used for downloading mods. (i.e. `fallout4` for Fallout 4)
- `launcher`: Specifies the supported launchers for the game (Steam, GOG, Epic Games).
  - `steam`: The Steam App ID for the game. *(Integer)*
  - `gog`: The GOG Galaxy ID for the game. *(Integer)*
  - `epic`: The Epic Games Store ID for the game. *(String)*
- `subdirectory`: The subdirectory name(s) for the game's installation in the launcher library.
- `executable`: The filename(s) of the game's executable file.
- `tricks`: A list of compatibility tricks to apply with proton-/winetricks during installation.
- `script_extenders`: A list of script extenders associated with the game. *([See below][script_extenders] for details)*
- `workarounds`: A list of workarounds to apply for the game. *([See below][workarounds] for details)*

### `subdirectory` and `executable` for different launcher paths
Some games may have different installation paths or executable names depending on the launcher used. In such cases, you can specify these fields as mappings for each launcher, rather than a single string.:

```yaml
    subdirectory:
      steam: <steam_subdirectory>
      gog: <gog_subdirectory>
      epic: <epic_subdirectory>
    executable:
      steam: <steam_executable>
      gog: <gog_executable>
      epic: <epic_executable>
```

### `script_extenders`
The `script_extenders` section allows you to define script extenders associated with the game. Each script extender can have its own set of properties, such as download URLs and installation instructions.

```yaml
    script_extenders:
      - version: <version>
        runtime:
          steam:
            - <runtime_version_1>
            - <runtime_version_2>
          gog:
            - <runtime_version_1>
          epic:
            - <runtime_version_1>
        download: # Further details below
        file_whitelist:
          - <file_1>
          - <file_2>
          - <directory/file_3>
          - <directory/subdirectory/file_4>
```

**Key Fields:**
- `version`: The version of the script extender.
- `runtime`: Specifies the compatible runtime versions for different launchers.
  - `steam`: A list of compatible Steam runtime versions.
  - `gog`: A list of compatible GOG runtime versions.
  - `epic`: A list of compatible Epic Games Store runtime versions.
- `download`: Defines how to download the script extender files. *([See below][script_extenders_download] for details)*
- `file_whitelist`: A list of files and directories to include in the script extender installation.

> ### `download`
> The `download` section within a script extender defines how to download the script extender files. It can include multiple download sources, each with its own URL and optional checksum for verification.
>
> ```yaml
>         download:
>           checksum: <checksum>
>           direct: <url>
>             url: <url>
>             checksum: <checksum>
>           nexus:
>             mod_id: <mod_id>
>             file_id: <file_id>
>             checksum: <checksum>
> ```
>
>
> **Key Fields:**
> - `checksum`: The SHA256 checksum of the downloaded file for verification. This can be specified at the top level (same as `direct` or `nexus`), or within each download if different checksums are required for each source.
> - `direct`: Specifies a direct download URL for the script extender. The URL can be provided either as a string (`direct: <url>`) or withing the `url` subfield (`direct: url: <url>`).
> - `nexus`: Specifies a Nexus Mods download for the script extender.
>   - `mod_id`: The Nexus Mods mod ID for the script extender.
>   - `file_id`: The specific file ID to download from the mod.
>
> ***Note:** At least one download source (`direct` or `nexus`) must be provided for each script extender.*

### `workarounds`
The `workarounds` section allows you to define specific workarounds to apply for the game during installation.

```yaml
    workarounds:
      - needs_java: true
      - single_executable: true
      - directories:
          - <directory_1>
          - <directory_2>
      - files:
        - <source>: <destination>
```

All workarounds defined here are optional and will only be applied if specified for the game.

**Key Fields:**
- `needs_java`: Indicates if the game or one of it's components (tools, mods, etc.) requires Java to run.
- `single_executable`: Indicates if the game uses a single executable file for launching. This will switch the backup file extension from `.exe.bak` to `.bak.exe` so the file is still usable.
- `directories`: A list of directories to create in the root of the game's installation folder.
- `files`: A list of files to add to the game's installation folder.
  - `<source>`: The source file name in the installer's `cfg/workarounds/` directory. ([`configs/`]`workarounds/` in the repository)
  - `<destination>`: The destination file name in the game's installation folder.

[script_extenders]: #script_extenders
[script_extenders_download]: #download
[workarounds]: #workarounds
[`configs/`]: https://github.com/furglitch/modorganizer2-linux-installer/tree/rewrite/configs
