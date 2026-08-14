---
title: update
layout: default
nav_order: 2
parent: CLI Guide
---

# `update`

Updates the MO2 executable and NXM handler for an existing instance, and refreshes its launch option.

```bash
mo2-lint update <directory> [options]
```

## Parameters

`<directory>` is required and must be the exact path to the instance.

## Options

`--mo2-archive <path>` + `--mo2-checksum <sha256>`
: [Unsupported / Advanced] Install MO2 from a local `.zip`/`.7z` archive instead of downloading the bundled version. Both flags are required together. The archive is verified against the checksum before extraction. Useful for offline installs or pinning a specific build.
  ```bash
  mo2-lint update /path/to/instance \
    --mo2-archive ~/Downloads/Mod.Organizer-2.5.2.7z \
    --mo2-checksum <sha256>
  ```
  The instance is automatically [pinned](./managing-instances.html#pin) afterward, so a later `update` won't overwrite your chosen build.

`--theme <name>`, `-t <name>`
: Apply a theme to the instance. See [Themes](./themes.html). Default settable via `[instance].theme`.

{: .warning }
> If the instance is **pinned**, `update` will not change the MO2 version. Either run `mo2-lint unpin <directory>` first, or supply `--mo2-archive`, which overrides the pin for that update (and re-pins the instance afterward).
