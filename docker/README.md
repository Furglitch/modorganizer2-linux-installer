# Docker Testing Environment

In order to validate that the installer works across different Linux distributions, a Docker testing environment has been set up. This allows for testing the installer in a controlled environment, without needing to set up multiple virtual machines or physical machines.

*This testing environment is not indicative of the actual user experience, and is only meant to validate that the installer can run and install Mod Organizer 2 on different distributions. It does not test for compatibility with different hardware or software configurations, or for any issues that may arise from running the installer on a real system.*

Currently, the testing environment includes the following distributions:
- Ubuntu
- Debian
- Fedora
- Arch Linux
- SteamOS

and tests the following games:
- The Elder Scrolls IV: Oblivion

## Usage

### Full Test

To build and run all tests, use the following command:

*All commands assume you are in the root directory of the project.*

```bash
docker compose -f "./docker/docker-compose.yml" up --build
```

After the tests have completed, you can review the results with the following command:

```bash
for container in mo2-lint-ubuntu mo2-lint-debian mo2-lint-arch mo2-lint-fedora mo2-lint-steamos; do
    echo "Logs for $container:"
    docker logs $container | tail -n 80
    echo "-----------------------------------"
done
```

### Individual Tests

To run a specific test, use the following command:

```bash
docker compose -f "./docker/docker-compose.yml" run --build --rm test-ubuntu
docker compose -f "./docker/docker-compose.yml" run --build --rm test-debian
docker compose -f "./docker/docker-compose.yml" run --build --rm test-arch
docker compose -f "./docker/docker-compose.yml" run --build --rm test-fedora
docker compose -f "./docker/docker-compose.yml" run --build --rm test-steamos
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
|           └── Games/                                      # Heroic pseudo-installs
|               ├── epic/                                       # Pseudo-installs for Epic games
|               └── gog/                                        # Pseudo-installs for GOG games
├── docker-compose.yml                                      # Docker Compose Configuration
├── dockerfile                                              # Dockerfile for building the image
├── entrypoint.sh                                           # Script to run on container start
├── gen_appinfo.py                                          # Script to convert plaintext appinfo.vdf to binary for Steam testing
└── validate.sh                                             # Script to validate the installation
```
