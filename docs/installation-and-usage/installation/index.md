---
title: Installation
layout: default
nav_order: 1
parent: Installation and Usage
---

# Installing MO2-LINT

Installation of MO2-LINT is straightforward. Follow the steps below to get started.

Download the latest release from the [GitHub Releases page]. The file is called `mo2-lint` (without any file extension).
<sub>Please note, only versions above 7.0.0 are supported.</sub>

Make the downloaded file executable. You can do this via the terminal with the command:
```bash
chmod +x path/to/downloaded/mo2-lint
```

After making the file executable, you can run MO2-LINT directly from the terminal:
```bash
path/to/downloaded/mo2-lint <command> [options]
```

### Installing to PATH (Optional)

It is recommended to move the executable to a directory included in your system's PATH, such as `/usr/local/bin`, for easier access:
```bash
sudo mv path/to/downloaded/mo2-lint /usr/local/bin/mo2-lint
```
If you are not sure what directories are in your PATH, you can check by running:
```bash
echo "$PATH" | tr ':' '\n'
```

You can now run MO2-LINT from the terminal by simply typing:
```bash
mo2-lint <command> [options]
```

For detailed usage instructions, refer to the [Usage](../usage/) page.

[GitHub Releases page]: https://github.com/furglitch/modorganizer2-linux-installer/releases
