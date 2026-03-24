# Docker Testing Environment

**WIP: The Docker testing environment is currently non-functional.**

In order to validate that the installer works across different Linux distributions, a Docker testing environment has been set up. This allows for testing the installer in a controlled environment, without needing to set up multiple virtual machines or physical machines.

## Usage

To build and run the Docker container, use the following command:

```bash
docker compose -f "./docker/docker-compose.yaml" run --build --rm test
# Assuming you are in the root directory of the project.
```

This will build the Docker image and run the container, and then remove the container once it exits.

## Architecture

```
├── filesystem/
|   └── home/
|       └── docker/
|           ├── .config/
|           |   └── heroic/
|           |       ├── GamesConfig/                # Heroic configs
|           |       |   └── *.json                      # Heroic-installed games list
|           |       ├── gog_store/                  # GOG configs
|           |       |   └── installed.json              # GOG-installed games list
|           |       ├── legendaryConfig/            # Epic configs
|           |       |   └── legendary/
|           |       |       └── installed.json          # Epic-installed games list
|           ├── games/                              # Game pseudo-installs
|           |   ├── epic/                               # Pseudo-installs for Epic games
|           |   ├── gog/                                # Pseudo-installs for GOG games
|           |   └── steam/                              # Pseudo-installs for Steam games
```
