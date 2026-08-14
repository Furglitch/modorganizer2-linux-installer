---
title: Adding a New Game
layout: default
nav_order: 4
parent: Contributing
---

# Adding a New Game

To add support for a new game:

1. Add an entry to `configs/game_info.yml`, following the structure in [Configuration Files](./configuration-files).
2. Test the installation using the [Docker test environment](./testing) or a local setup.
3. If the game needs special steps or known workarounds, add a [Game Guide](../game-guides/) under `docs/game-guides/` and link it from the [Game Guides index](../game-guides/).
4. Follow the [Pull Request Guidelines](./pull-requests) when submitting your change.
