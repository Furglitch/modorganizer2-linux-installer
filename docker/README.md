# Docker Testing Environment

**WIP: The Docker testing environment is currently non-functional.**

In order to validate that the installer works across different Linux distributions, a Docker testing environment has been set up. This allows for testing the installer in a controlled environment, without needing to set up multiple virtual machines or physical machines.

## Usage

To build and run the Docker container, use the following command:

```bash
docker compose -f "./docker/docker-compose.yml" run --build --rm test
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
|           |       ├── GamesConfig/                        # Heroic configs
|           |       |   └── *.json                              # Heroic-installed games list
|           |       ├── gog_store/                          # GOG configs
|           |       |   └── installed.json                      # GOG-installed games list
|           |       ├── legendaryConfig/legendary/          # Epic configs
|           |       |   └── installed.json                      # Epic-installed games list
|           |       └── store_cache/                        # Epic configs
|           |           └── legendary_install_info.json         # Epic-installed games list
|           ├── .local/share/Steam                          # Steam pseudo-installs
|           ├── Games/                                      # Heroic pseudo-installs
|           |   ├── epic/                                       # Pseudo-installs for Epic games
|           |   ├── gog/                                        # Pseudo-installs for GOG games
├── docker-compose.yml                                      # Docker Compose Configuration
├── dockerfile                                              # Dockerfile for building the image
├── entrypoint.sh                                           # Script to run on container start
├── gen_appinfo.py                                          # Script to convert plaintext appinfo.vdf to binary for Steam testing
├── validate.sh                                             # Script to validate the installation
```
