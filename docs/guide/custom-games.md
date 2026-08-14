---
title: Custom Games
layout: default
nav_order: 6
parent: CLI Guide
---

# Custom Games

{: .unsupported }
> Adding custom games is **not supported**. There are too many variables to account for, and there is no guarantee the installation or game will work. This is intended for advanced users comfortable troubleshooting issues themselves. Use at your own risk.

The `install` command supports custom games via the `--custom` flag, pointing to a custom [game_info YAML file](https://github.com/Furglitch/modorganizer2-linux-installer/blob/main/configs/game_info.yml) that defines them.

```bash
mo2-lint install --custom ~/my_custom_games.yaml <game> <directory>
```

For the structure of the custom game definition file, see [Configuration Files](../contributing/configuration-files) in the Contributing section.
