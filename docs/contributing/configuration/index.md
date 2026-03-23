---
title: Configuration Files
layout: default
nav_order: 1
parent: Contributing
---

# Configuration Files

MO2-LINT uses YAML configuration files to define various resources for the installer, such as supported games. These configuration files are located in the [`configs/`] directory of the project.

**About `schema`:** Each configuration file includes a `schema` field at the top. This field indicates the earliest version of MO2-LINT that can utilize that configuration file. This is to ensure that if we add or remove fields in the future, older versions of the installer won't attempt to use incompatible configuration files. If a configuration file has a `schema` version higher than the current installer version, the installer will skip that file and not download updates for it.

## `games_info.yml`

The `games_info.yml` file contains information about the supported games, including their names, executable paths, and any specific configurations required for installation. The structure of the file is as follows:

```yaml
schema:

games:

  <game_id>:
    display_name: <display_name>
    nexus_slug: <nexus_slug>
    launcher_ids:
      steam: <steam>
      gog: <gog>
      epic: <epic>
    subdirectory: <subdirectory>
    executable: <executable>
    tricks:
      - <trick_1>
      - <trick_2>
    launch_options: # Further details below
    script_extenders: # Further details below
    workarounds: # Further details below
```

| Field | Required | Description |
| --- | --- | --- |
| `game_id` | Yes | Unique identifier. Used in the CLI. |
| `display_name` | Yes | Human-readable name of the game. |
| `nexus_slug` | Yes | Nexus Mods slug for the game. (i.e. `fallout4` for Fallout 4) |
| `launcher_ids` | Yes | Supported launchers and their IDs. [See below](#launcher_ids) for more details. |
| `subdirectory` | Yes | Subdirectory name(s) for the game's installation in the launcher library. [See below](#subdirectory-and-executable-for-different-launcher-paths) for more details. |
| `executable` | Yes | Filename(s) of the game's executable file. [See below](#subdirectory-and-executable-for-different-launcher-paths) for more details. |
| `tricks` | No | List of "tricks" to apply with proton-/winetricks during installation. |
| `launch_options` | No | Specifications for Steam launch options. [See below](#launch_options) for more details. |
| `script_extenders` | No | List of script extenders associated with the game. [See below](#script_extenders) for more details. |
| `workarounds` | No | List of workarounds to apply for the game. [See below](#workarounds) for more details. |

### `launcher_ids`
The `launcher_ids` field specifies the supported launchers for the game and their corresponding IDs. The supported launchers are Steam, GOG, and Epic Games Store. Each launcher has its own unique ID.

```yaml
    launcher_ids:
      steam: <steam_app_id> # integer
      gog: <gog_galaxy_id> # integer
      epic: <epic_game_id> # string
```

### `subdirectory` and `executable` for different launcher paths
Some games may have different installation paths or executable names depending on the launcher used. In such cases, you can specify these fields as mappings for each launcher, rather than a single string.

```yaml
    # All launchers
    subdirectory: <subdirectory>
    executable: <executable>

OR

    # Per-launcher
    subdirectory:
      steam: <steam_subdirectory>
      gog: <gog_subdirectory>
      epic: <epic_subdirectory>
    executable:
      steam: <steam_executable>
      gog: <gog_executable>
      epic: <epic_executable>

# Not interchangable. You can either specify a single value or per-launcher values, but not both.
```

### `launch_options`
The `launch_options` field allows you to specify custom launch options for the game when launched through Steam.

```yaml
    launch_options:
      label: <label>
      arguments:
        - <argument_1>
        - <argument_2>
      type: <type>
      oslist:
        - <os_1>
        - <os_2>
      osarch: <osarch>
```

| Field | Required | Description | Default | Options |
| --- | --- | --- | --- | --- |
| `label` | No |The label to display for the launch option in Steam. | "Launch Mod Organizer" |  |
| `arguments` | If Applicable | A list of command-line arguments to pass when launching the game through Steam. |  |  |
| `type` | No | The type of launch option. | `OPTION3` | `default`, `none`, `vr`, `OPTION1`, `OPTION2`, and `OPTION3`. |
| `oslist` | If Applicable | A list of operating systems to apply the launch options for. If not specified, the launch options will be applied for all operating systems. |  |  |
| `osarch` | If Applicable | The operating system architecture to apply the launch options for. Available options are '32' and '64'. |  | '32', '64' |

### `script_extenders`
The `script_extenders` section allows you to define script extenders associated with the game. Each script extender can have its own set of properties, such as download URLs and installation instructions.

```yaml
    script_extenders:
      - version: <version>
        runtime: # Further details below
        download: # Further details below
        file_whitelist:
          - <file_1>
          - <file_2>
          - <directory/file_3>
          - <directory/subdirectory/file_4>
```

| Field | Required | Description |
| --- | --- | --- |
| `version` | Yes | The version of the script extender. |
| `runtime` | Yes | Compatible runtime version. [See below](#runtime) for more details. |
| `download` | Yes | Download information for the script extender. [See below](#download) for more details. |
| `file_whitelist` | No | A list of files and directories to include in the script extender installation. If not specified, all files will be included. |

> ### `runtime`
> The `runtime` field specifies the compatible runtime versions for different launchers. This can either be a single version string that applies to all launchers, or a list of per-launcher version strings. The installer will use this information to determine which script extender version to install based on the runtime version of the game instance.
>
> ```yaml
>     runtime: <version> # Applies to all launchers
>
> OR
>
>     runtime:
>       steam:
>         - <steam_runtime_version_1>
>         - <steam_runtime_version_2>
>       gog:
>         - <gog_runtime_version_1>
>         - <gog_runtime_version_2>
>       epic:
>         - <epic_runtime_version_1>
>         - <epic_runtime_version_2>
> ```

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
> | Field | Required | Description |
> | --- | --- | --- |
> | `checksum` | No | The SHA256 checksum of the downloaded file for verification. This can be specified at the top level to be applied to both direct and Nexus downloads, or per download type |
> | `direct` | or Nexus | Specifies a direct download URL for the script extender. The URL can be provided either as a string (`direct: <url>`), or within the `url` subfield (`direct: url: <url>`) if specify type-specific checksums. |
> | `nexus` | or Direct | Specifies a Nexus Mods download for the script extender. Requires both `mod_id` and `file_id` to be specified. |
>
> ***Note:** At least one download source (`direct` or `nexus`) must be provided for each script extender.*

### `workarounds`
The `workarounds` section allows you to define specific workarounds to apply for the game during installation.

```yaml
    workarounds:
      - needs_java: true
      - directories:
          - <directory_1>
          - <directory_2>
      - files:
        - <source>: <destination>
```

All workarounds defined here are optional and will only be applied if specified for the game.

| Field | Required | Description | Default |
| --- | --- | --- |
| `needs_java` | No | Indicates if the game or one of its components (tools, mods, etc.) requires Java to run. | false |
| `directories` | No | A list of directories to create in the root of the game's installation folder. |  |
| `files` | No | A list of files to add to the game's installation folder. Each file is specified as a mapping of a source file (located in the installer's `cfg/workarounds/` directory) to a destination file in the game's installation folder. |  |

### Children
You can specify child configurations as well, which allows a game to 'adopt' the properties of another game. This is mostly used for games with alternate languages (i.e. New Vegas's Russian variant) or alternate editions (i.e. Fallout 3's GOTY edition). Child configurations can override any of the parent properties as needed. Any property not specified in the child will be inherited from the parent.

```yaml
    <game_id>:
      parent: <parent_game_id>
      display_name: <display_name>
      nexus_slug: <nexus_slug>
      launcher_ids:
        steam: <steam>
        gog: <gog>
        epic: <epic>
      [...other properties as needed...]
```


## `resource_info.yml`

The `resource_info.yml` file contains information about various resources used by the installer; currently Mod Organizer 2 itself, Java, and Winetricks. The structure of the file is as follows:

```yaml
schema:

resources:

  <resource>:
    version: <version>
    download_url: <download_url>
    checksum: <checksum>
    path_internal: <path_internal>
    checksum_internal: <checksum_internal>
```

| Field | Required | Description |
| --- | --- | --- |
| `resource` | Yes | Unique identifier. |
| `version` | Yes | The version of the resource. |
| `download_url` | No | The direct download URL for the resource. |
| `checksum` | No | The SHA256 checksum of the downloaded file for verification. |
| `path_internal` | No | Relative path to the main executable or relevant file within the downloaded archive. |
| `checksum_internal` | No | The SHA256 checksum of the internal file specified in `path_internal` for verification after extraction. |

## `plugin_info.yml`

The `plugin_info.yml` file contains information about the plugins used by the installer, such as their versions and download URLs. The structure of the file is as follows:

```yaml
schema:

plugins:

  <plugin>: <manifest_url>
```

| Field | Required | Description |
| --- | --- | --- |
| `plugin` | Yes | Unique identifier for the plugin. |
| `manifest_url` | Yes | The URL to the plugin's manifest file. This must point directly to the raw file. The manifest file must be a JSON file following the manifest structure created by [@Kezyma] for their 'Plugin Finder' plugin. For more details on this schema, please refer to the documentation for [Kezyma's Plugin Finder]. |

[`configs/`]: https://github.com/furglitch/modorganizer2-linux-installer/tree/rewrite/configs
[@Kezyma]: https://github.com/Kezyma
[Kezyma's Plugin Finder]: https://github.com/Kezyma/ModOrganizer-Plugins/blob/main/docs/pluginfinder.md#adding-your-plugin
