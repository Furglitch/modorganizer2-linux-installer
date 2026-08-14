---
title: Testing
layout: default
nav_order: 2
parent: Contributing
---

# Testing

MO2-LINT includes a Docker-based test environment that validates the installer against multiple Linux distributions.

These tests are run automatically on every pull request, but you can also run them locally to verify your changes before submitting a PR.

You can also run the tests on your own machine without Docker by following the [Getting Started](../getting-started/) and [CLI Guide](../guide/) instructions.

## Run the full suite

```bash
docker compose -f "./docker/docker-compose.yml" up --build
```

## Run a single distribution

```bash
docker compose -f "./docker/docker-compose.yml" run --build --rm test-ubuntu
docker compose -f "./docker/docker-compose.yml" run --build --rm test-arch
docker compose -f "./docker/docker-compose.yml" run --build --rm test-fedora
docker compose -f "./docker/docker-compose.yml" run --build --rm test-debian
docker compose -f "./docker/docker-compose.yml" run --build --rm test-steamos
```

For more detail on the test environment itself, see the [Docker README](https://github.com/furglitch/modorganizer2-linux-installer/blob/main/docker/README.md).
