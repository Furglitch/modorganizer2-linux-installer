---
title: Adding Custom Games
layout: default
nav_order: 1
parent: Usage
---

# Adding Custom Games

> ## Warning
> Adding custom games is not supported, as there are too many variables to account for. There is no guarantee that the installation or game will work properly. Use at your own risk.<br>
> This guide is intended for advanced users who are comfortable with troubleshooting potential issues that may arise

The `install` command supports adding custom games via the `--custom-game` (`-c`) flag. This flag takes a path to a YAML file that defines the custom games.

For example, to load a custom game definition file located at `~/my_custom_games.yaml`, you would run:

```bash
mo2_lint install -c ~/my_custom_games.yaml
```

More information on the structure of the custom game definition file can be found in the [Configuration Files] section of the contributing guide.

[Configuration Files]: ../../../contributing/configuration/
