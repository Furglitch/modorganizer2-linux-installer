---
title: Pull Request Guidelines
layout: default
nav_order: 3
parent: Contributing
---

# Pull Request Guidelines

Before submitting a pull request:

1. Ensure your changes pass all pre-commit checks (these run automatically if you've set up pre-commit hooks. See [Development Environment](./dev-environment)).
2. Follow [Conventional Commits](https://www.conventionalcommits.org/) for your commit messages. These are enforced by the pre-commit hooks and GitHub Actions.
3. Keep pull requests focused. One feature or fix per PR.
4. If your change affects a supported game or adds a new one, include relevant documentation updates.
5. If adding a new game, ensure the game info entry is added to `configs/game_info.yml` following [Configuration Files](./configuration-files). See [Adding a New Game](./adding-a-game).

{: .note }
> You are not required to label your pull request. It will be labeled automatically by GitHub Actions based on your PR title and body.
