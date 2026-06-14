---
title: Contributing
layout: default
nav_order: 5
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

Install the following dependencies if you don't have them already:
- Python 3.13
- [`uv`](https://docs.astral.sh/uv/getting-started/installation/#cargo)
- `make`
- Wine (for building the redirector)

### Installation
To set up your development environment, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/Furglitch/modorganizer2-linux-installer
   cd modorganizer2-linux-installer
   ```
2. Install pre-commit hooks:
   ```bash
   uv run pre-commit install
   ```

### Running the Application

To run the application directly from source:

```bash
make run ARGS="<installer arguments>"
```

Where ARGS *must* be all caps, and `<installer arguments>` are the same as the command-line arguments you would use when running the installer normally. For example:

```bash
make run ARGS="install skyrim /path/to/install"
# represents `mo2-lint install skyrim /path/to/install`
```

> **Note:** The application requires the Redirector and NXM handler binaries to be present. Run a build first before running from source.

To build all components:

```bash
make _build
```

To build individual components:

```bash
make redirector
make nxm-handler
make mo2-lint_only
```

## Testing

MO2-LINT includes a Docker-based test environment that validates the installer against multiple Linux distributions. To run the full test suite:

```bash
docker compose -f "./docker/docker-compose.yml" up --build
```

To run a test for a specific distribution:

```bash
docker compose -f "./docker/docker-compose.yml" run --build --rm test-ubuntu
docker compose -f "./docker/docker-compose.yml" run --build --rm test-arch
docker compose -f "./docker/docker-compose.yml" run --build --rm test-fedora
docker compose -f "./docker/docker-compose.yml" run --build --rm test-debian
docker compose -f "./docker/docker-compose.yml" run --build --rm test-steamos
```

For more details on the test environment, see the [Docker README](https://github.com/furglitch/modorganizer2-linux-installer/blob/main/docker/README.md).

## Pull Request Guidelines

Before submitting a pull request:

1. Ensure your changes pass all pre-commit checks (these run automatically if you set up pre-commit hooks).
2. Follow [Conventional Commits](https://www.conventionalcommits.org/) for your commit messages.
3. Keep pull requests focused. One feature or fix per PR.
4. If your change affects a supported game or adds a new game, include relevant documentation updates.
5. If you are adding a new game, ensure the game info entry is added to `configs/game_info.yml` following the structure defined in [Configuration Files](./configuration/).

## Adding a New Game

To add support for a new game:

1. Add an entry to `configs/game_info.yml` following the structure in [Configuration Files](./configuration/).
2. Test the installation using the Docker test environment or a local setup.
3. If the game requires special steps or known workarounds, add a [game-specific guide](../usage/game-specific/) under `docs/usage/game-specific/` and link it from the [index](../usage/game-specific/).
