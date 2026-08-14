---
title: Contributing
layout: default
nav_order: 7
has_children: true
description: "How to contribute to MO2-LINT."
---

# Contributing to MO2-LINT

Contributions are welcome! This section covers everything needed to get set up, make a change, and submit it.

## Guidelines

To keep the codebase consistent, we use pre-commit hooks and GitHub Actions for formatting and validation, including:

- Ruff linting (code formatting check)
- Private key detection
- Trailing whitespace trimmer
- YAML formatting checks
- EOF newline checks
- File size limiter (currently 150kb)
- Branch committing restrictions
- Conventional commit message checks

These checks run automatically on every pull request, in case any are missed locally (or you don't have pre-commit hooks set up).

Pull requests that fail on any of these checks will not be accepted or reviewed until the issues are resolved.

## Where to go next

| Page | Covers |
|:--|:--|
| [Development Environment](./dev-environment) | Prerequisites, cloning, running from source, building. |
| [Testing](./testing) | The Docker-based multi-distro test suite. |
| [Pull Request Guidelines](./pull-requests) | What to check before opening a PR. |
| [Adding a New Game](./adding-a-game) | Steps to add support for a new game. |
| [Configuration Files](./configuration-files) | Reference for the YAML files under `configs/`. |
