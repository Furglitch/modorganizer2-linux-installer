# Steam Redirector

Small program designed to trick the Steam Client into running an arbitrary executable when launching a specific game.

This is necessary for using Mod Organizer 2 with Proton versions utilizing the newer Steam Runtime (Soldier). The problem and the thought process behind this solution are described in details in [#275](https://github.com/rockerbacon/modorganizer2-linux-installer/issues/275).

## How it works

The redirector will read a file location stored in `modorganizer2/instance_path.txt` (relative to the working directory) and execute it. If the redirector is put in place of the game's executable, it will force the Steam Client to execute whatever is in `modorganizer2/instance_path.txt`.

## Compiling

The following compilation instructions are for Linux systems only.

Note that the Windows binaries are statically linked. This is necessary for proper execution under Wine without installing additional MinGW libraries.

### Requirements

You'll need the following:

- gcc
- make
- Mingw64

#### Fedora 35

```
sudo dnf install gcc make mingw64-gcc
```

#### Arch

```
sudo pacman -S gcc make mingw-w64-gcc
```

Check MinGW's [downloads page](https://www.mingw-w64.org/downloads/) for a more complete list of available packages.

### Compile Commands

A Makefile is provided for simplifying the whole process.

- Running `make` or `make main.exe` will compile Windows binaries - these are the ones you want for the MO2 installer
- Running `make main` will compile Linux binaries
- Running `make all` will compile all binaries
