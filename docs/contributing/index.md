---
title: Contributing
layout: default
nav_order: 1
parent: Mod Organizer 2 Linux Installer
---

# Contributing to MO2-LINT

Contributions to Mod Organizer 2 Linux Installer (MO2-LINT) are welcome! If you would like to contribute, please read the following guide for more information on how to get involved.

## Guidelines
In order to maintain consistency across the codebase, we utilize pre-commit hooks and GitHub Actions for formatting and validation.

These include:
- Ruff linting (code formatting check)
- Private key detection
- Trailing whitespace trimmer
- YAML formatting checks
- EOF newline checks
- File size limiter (currently 150kb)
- Branch committing restrictions
- Conventional commit message checks

These commit checks will run when you make a pull request, in case any are missed locally (or you don't have pre-commit hooks set up)

## Setting Up Your Development Environment

### Prerequisites
This project is developed using *Python 3.13*, so please ensure you have this version installed.

### Installation
To set up your development environment, follow these steps:

1. Install Python 3.13, [`uv`](https://docs.astral.sh/uv/getting-started/installation/#cargo), and `make` if you don't have it already.
2. Clone the repository:
   ```bash
   git clone https://github.com/Furglitch/modorganizer2-linux-installer -b rewrite
   cd modorganizer2-linux-installer
   ```
3. Install pre-commit hooks:
   ```bash
   uv run pre-commit install
   ```

### Running the Application
To run the application, use the following command:
```bash
uv run src/mo2-lint/__init__.py
```

To build the application, use:
```bash
make _build
```
