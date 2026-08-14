---
title: Installation Issues
layout: default
nav_order: 1
parent: Troubleshooting
---

# Installation Issues

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Download error

If MO2-LINT fails to download a required file, check your internet connection and retry. If it persists, run with more verbosity:

```bash
mo2-lint install <game> <directory> --log-level DEBUG # or TRACE
```

## Game not found

MO2-LINT searches your Steam and Heroic libraries for the specified game. If it can't find the game:

- Make sure it's installed and visible in your launcher.
- You **must** launch it at least once before running MO2-LINT. This initializes the Proton prefix.
- If installed in a non-standard location, verify the launcher is able to see that library path. This is a common issue with sandboxed installations like Flatpak or Snap.
- If you have a copy of the game installed in both Steam and Heroic, disambiguate with `--launcher`:
  ```bash
  mo2-lint install <game> <directory> --launcher steam
  ```

## Permission denied

Check you have write access to the target directory:

```bash
ls -ld /path/to/instance
```

If it's owned by root or another user, either pick a different directory or fix ownership with `chown`.

## Script extender not detected by MO2

If MO2 doesn't show the script extender as an executable option:

1. Verify it was installed into the **game directory**, not the MO2 instance directory.
2. In MO2, check the executables list. Add it manually if missing, pointing at the script extender executable in the game folder.
3. If `--script-extender` was used but the file is missing, re-run with `--log-level DEBUG` and check the log for download/extraction errors.

## Script extender crashes on launch

Some script extender plugins require native Windows DLLs that may not work correctly under Proton. Check [GitHub Issues](https://github.com/furglitch/modorganizer2-linux-installer/issues) for game-specific workarounds, and the relevant [Game Guide](../game-guides/) for your game.
