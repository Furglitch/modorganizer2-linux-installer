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
- 'requirements.txt' validation
- EOF newline checks
- File size limiter (currently 150kb)
- Branch committing restrictions
- Conventional commit message checks

## Setting Up Your Development Environment

### Prerequisites
This project is developed using *Python 3.13*, so please ensure you have this version installed.

### Installation
To set up your development environment, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/Furglitch/modorganizer2-linux-installer -b rewrite
   cd modorganizer2-linux-installer
   ```
2. Create a virtual environment and activate it:
   ```bash
   python -m venv ./venv
   source ./venv/bin/activate
   ```
3. Install the required dependencies:
   ```bash
   pip install -r ./requirements.txt
   ```
4. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```
