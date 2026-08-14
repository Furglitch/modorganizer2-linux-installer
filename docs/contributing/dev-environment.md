---
title: Development Environment
layout: default
nav_order: 1
parent: Contributing
---

# Development Environment

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Prerequisites

- Python 3.13
- [`uv`](https://docs.astral.sh/uv/getting-started/installation/#cargo)
- `make`
- Wine (for building the redirector)

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/Furglitch/modorganizer2-linux-installer
   cd modorganizer2-linux-installer
   ```
2. Install pre-commit hooks:
   ```bash
   uv run pre-commit install
   ```

## Running from source

```bash
make run ARGS="<installer arguments>"
```

`ARGS` must be all caps. `<installer arguments>` are the same as normal CLI arguments, for example:

```bash
make run ARGS="install skyrim /path/to/install"
# represents `mo2-lint install skyrim /path/to/install`
```

{: .note }
> Running from source requires the Redirector and NXM handler binaries to already be built, otherwise errors *will* occur. Build them first with `make nxm-handler` and `make redirector`.

## Building

Build everything:

```bash
make _build
```

Or build individual components:

```bash
make redirector
make nxm-handler
make mo2-lint_only
```

## Next step

Set up the [test environment](./testing) before submitting changes.
