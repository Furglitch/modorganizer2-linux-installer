---
title: Configuration Files
layout: default
nav_order: 5
parent: Contributing
---

# Configuration Files

MO2-LINT uses YAML configuration files to define resources for the installer, such as supported games. These live in the [`configs/`](https://github.com/furglitch/modorganizer2-linux-installer/tree/main/configs) directory of the project.

{: .note }
> **About `schema`:** Every configuration file includes a `schema` field indicating the earliest MO2-LINT version that can use it. If a file's `schema` is higher than the current installer version, the installer skips it and doesn't download updates for it. This keeps older installer versions from breaking on config fields they don't understand.

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## `game_info.yml`

Defines supported games. Includes names, executable paths, and installation specifics.

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
    launch_options: # see below
    script_extenders: # see below
    workarounds: # see below
```

| Field | Required | Description |
|:--|:--|:--|
| `game_id` | Yes | Unique identifier. Used in the CLI. |
| `display_name` | Yes | Human-readable name of the game. |
| `nexus_slug` | Yes | Nexus Mods slug (e.g. `fallout4` for Fallout 4). |
| `launcher_ids` | Yes | Supported launchers and their IDs. See [`launcher_ids`](#launcher_ids). |
| `subdirectory` | Yes | Subdirectory name(s) in the launcher library. See [below](#subdirectory-and-executable-for-different-launcher-paths). |
| `executable` | Yes | Filename(s) of the game's executable. See [below](#subdirectory-and-executable-for-different-launcher-paths). |
| `tricks` | No | "Tricks" to apply with proton-/winetricks during installation. |
| `launch_options` | No | Steam launch option specifications. See [`launch_options`](#launch_options). |
| `script_extenders` | No | Script extenders associated with the game. See [`script_extenders`](#script_extenders). |
| `workarounds` | No | Workarounds to apply for the game. See [`workarounds`](#workarounds). |

### `launcher_ids`

Supported launchers and their IDs:

```yaml
    launcher_ids:
      steam: <steam_app_id> # integer
      gog: <gog_galaxy_id> # integer
      epic: <epic_game_id> # string
```

### `subdirectory` and `executable` for different launcher paths

Some games have different install paths or executable names per launcher.

Specify as mappings instead of a single string:

```yaml
    subdirectory: <subdirectory>
    executable: <executable>
```

or as per-launcher mappings:

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

{: .warning }
> Per-launcher mappings and single-string versions cannot be mixed. If you use per-launcher mappings for either `subdirectory` or `executable`, you must specify all supported launchers for that field.

### `launch_options`

Custom Steam launch options for the game:

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
|:--|:--|:--|:--|:--|
| `label` | No | Label shown for the launch option in Steam. | "Launch Mod Organizer" | |
| `arguments` | If applicable | Command-line arguments passed on launch. | | |
| `type` | No | Launch option type. | `OPTION3` | `default`, `none`, `vr`, `OPTION1`, `OPTION2`, `OPTION3` |
| `oslist` | If applicable | Operating systems to apply the option for. Applies to all if unset. | | |
| `osarch` | If applicable | Architecture to apply the option for. | | `32`, `64` |

### `script_extenders`

```yaml
    script_extenders:
      - version: <version>
        runtime: # see below
        download: # see below
        file_whitelist:
          - <file_1>
          - <file_2>
          - <directory/file_3>
          - <directory/subdirectory/file_4>
```

| Field | Required | Description |
|:--|:--|:--|
| `version` | Yes | Script extender version. |
| `runtime` | Yes | Compatible runtime version. See [`runtime`](#runtime). |
| `download` | Yes | Download info. See [`download`](#download). |
| `file_whitelist` | No | Files/directories to include. Defaults to all files. |

#### `runtime`

Compatible runtime version(s) per launcher. Can be a single string applying to all launchers, or per-launcher lists. MO2-LINT displays this to the user for them to select from.

```yaml
    runtime: <version> # Applies to all launchers

    # OR
    runtime:
      steam:
        - <steam_runtime_version_1>
        - <steam_runtime_version_2>
      gog:
        - <gog_runtime_version_1>
        - <gog_runtime_version_2>
      epic:
        - <epic_runtime_version_1>
        - <epic_runtime_version_2>
```

#### `download`

How to download the script extender files, with optional per-source checksums:

```yaml
        download:
          checksum: <checksum>
          direct: <url>
            url: <url>
            checksum: <checksum>
          nexus:
            mod: <mod_id>
            file: <file_id>
            checksum: <checksum>
```

| Field | Required | Description |
|:--|:--|:--|
| `checksum` | No | SHA256 checksum for verification. Top-level applies to both direct and Nexus, or set per download type. |
| `direct` | or Nexus | Direct download URL. Either a plain string (`direct: <url>`) or, with a type-specific checksum, `direct: url: <url>`. |
| `nexus` | or Direct | Nexus Mods download. Requires both `mod` and `file` (mod ID and file ID). |

{: .note }
> At least one download source (`direct` or `nexus`) must be provided for each script extender.

{: .warning }
> Either set the top-level `checksum` for both download types, or set a type-specific checksum. Do not mix the two. `download.checksum` cannot be used with `download.direct.checksum` or `download.nexus.checksum`.

### `workarounds`

```yaml
    workarounds:
      - needs_java: true
      - directories:
          - <directory_1>
          - <directory_2>
      - files:
        - <source>: <destination>
```

All workaround fields are optional and applied only if specified.

| Field | Required | Description | Default |
|:--|:--|:--|:--|
| `needs_java` | No | Whether the game or a component requires Java. | `false` |
| `directories` | No | Directories to create in the game's install root. | |
| `files` | No | Files to add to the game's install folder, as `source` (in the installer's `cfg/workarounds/` directory) → `destination` mappings. | |

### Children

Game entries can specify a `parent`, inheriting its properties. Used mostly for alternate languages (e.g. New Vegas's Russian variant) or editions (e.g. Fallout 3's GOTY edition). Children can override any parent property; anything unspecified is inherited.

```yaml
    <game_id>:
      parent: <parent_game_id>
      display_name: <display_name>
      nexus_slug: <nexus_slug>
      launcher_ids:
        steam: <steam>
        gog: <gog>
        epic: <epic>
      # ...other properties as needed
```

## `resource_info.yml`

Defines other installer resources for downloading. Currently Mod Organizer 2 itself, Java, and Winetricks.

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
|:--|:--|:--|
| `resource` | Yes | Unique identifier. |
| `version` | Yes | Resource version. |
| `download_url` | No | Direct download URL. |
| `checksum` | No | SHA256 checksum for verification. |
| `path_internal` | No | Relative path to the main executable/relevant file within the downloaded archive. |
| `checksum_internal` | No | SHA256 checksum of the internal file at `path_internal`, verified after extraction. |

## `plugin_info.yml`

Defines plugins used by the installer.

```yaml
schema:

plugins:

  <plugin>: <manifest_url>
```

| Field | Required | Description |
|:--|:--|:--|
| `plugin` | Yes | Unique plugin identifier. |
| `manifest_url` | Yes | URL to the plugin's manifest file. Must point directly to the raw file, following the manifest structure created by [@Kezyma](https://github.com/Kezyma) for their "Plugin Finder" plugin. See [Kezyma's Plugin Finder docs](https://github.com/Kezyma/ModOrganizer-Plugins/blob/main/docs/pluginfinder.md#adding-your-plugin) for the schema. |

## `theme_info.yml`

Defines themes available via `--theme`/`-t` on [`install`](../guide/install.html) and [`update`](../guide/update.html).

```yaml
schema:

themes:

  <theme_slug>:
    stylesheet: <stylesheet_filename>
    parent: <parent_theme_slug>
    root: <root_subdirectory>
    nexus:
      slug: <nexus_game_slug>
      mod_id: <mod_id>
      file_id: <file_id>
```

| Field | Required | Description |
|:--|:--|:--|
| `theme_slug` | Yes | Unique theme identifier, used with `--theme`. |
| `stylesheet` | No | `.qss` stylesheet filename applied by the theme. Inherited from `parent` if unset. |
| `parent` | No | Another theme slug to inherit unset fields from (e.g. `stylesheet`, `nexus`, `root`). Used for palette variants of the same download, such as `fluency-midnight` inheriting from `fluency-dark`. |
| `root` | No | Subdirectory inside the downloaded Nexus archive containing the stylesheet. Only relevant for Nexus-sourced themes. |
| `nexus` | No | Nexus Mods download info for themes not bundled with MO2. Requires `mod_id` and `file_id`; `slug` (the Nexus game slug) is required unless inherited via `parent`. Omit entirely for themes already included with MO2. |
