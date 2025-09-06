# Custom Games

Games that aren't officially supported by this project may be installed using a custom game information script.

_Note that no support will be offered for these games outside of issues with the installer itself. We will not provide support for the games or MO2 themselves._

In order to install a custom game, create a game information script as described below, and run `install.sh -c path/to/your/script.sh`.

## Custom Game Information Script

Game information is defined in the form of a script file that sets a handful of variables.

For example, let's consider the included `dragonage.sh` game info script and a Steam library located in `/home/warden/.local/share/Steam/steamapps/common/`:

**`dragonage.sh`**
```bash
game_steam_subdirectory="Dragon Age Ultimate Edition"
game_nexusid="dragonage"
game_appid=47810
game_executable="DAOriginsLauncher.exe"
game_protontricks=("xaudio2_7=native" "d3dcompiler_43" "d3dx9")
game_scriptextender_url=""
game_scriptextender_files=""
```

- **`game_steam_subdirectory`** [required]: The path to the directory containing the game's executable.
- **`game_nexusid`**: The game's ID on Nexus Mods.

  If you don't know what this is, it can easily be obtained by visiting the game's mod page and looking at the URL. For example, **Dragon Age Ultimate Edition**'s URL is `https://www.nexusmods.com/games/dragonage`, and thus the `game_nexusid` is `dragonage`.

- **`game_appid`** [required]: The game's Steam ID.

  If you don't know what this is, it can easily be obtained by visiting the game's store page and looking at the URL. For example, **Dragon Age Ultimate Edition**'s URL is `https://store.steampowered.com/app/47810/Dragon_Age_Origins__Ultimate_Edition/`, and thus the `game_appid` is `47810`.

- **``game_executable``** [required]: The name of the game's main executable, including the file extension.

- **`game_protontricks`**: An array of settings to apply and/or system libraries to install in the game's Proton prefix. Each entry should be quoted and separated by a space.

    **NOTES**:
  - You might not actually need to do this. If the game runs well directly from Steam, it's already taken care of any dependencies.
  - The `arial` font is installed automatically.
  - This will likely require some experimentation. If you find that you missed a requirement, you should be able to install it after the fact using the **Protontricks** utility.

  A good place to find these is [Lutris' website](https://lutris.net) in the install scripts. Look for a section like:

  ```yaml
  installer:
  - task:
      app: arial d3dcompiler_43 d3dcompiler_47 d3dx9
      name: winetricks
  ```
  and use the list from `app`;

  ```bash
  game_protontricks=("d3dcompiler_43" "d3dcompiler_47" "d3dx9")
  ```

- **`game_scriptextender_url`**: A URL from which to download a script extender. You may have better luck installing this manually, depending on how the extender works.

- **`game_scriptextender_files`**: A list of specific files to install from the script extender, separated by spaces; _or_ `*` to install all files.

## Workarounds

Some games may require additional arbitrary changes to work properly or to resolve issues. In this case, you may supply a script to do just that with the argument `-w path/to/your/workaround.sh`.