# Post Installation

Additional steps you may want to take after installing Mod Organizer 2.

## Launch Options
Remember, when adding anything to your Launch Options, include the `%command%` argument. If it's part of the game (i.e. `--skip-launcher`) then it goes after, otherwise it goes before. Other than that, ordering doesn't really matter. For example:
```bash
BEFORE=true %command% --after
```
<sup>The above is only an example, not actual arguments</sup>

### Accessing/Installing outside of $HOME
When installing Mod Organizer 2 outside of your `$HOME` directory, you may encounter issues launching it due to Steam's Proton compatibility layer not being able to access the files. To resolve this, you can set the `STEAM_COMPAT_MOUNTS` environment variable in your game's Launch Options.

This can also be used to mount additional folders for Mod Organizer 2 to access, such as a folder containing external tools or scripts.

```bash
STEAM_COMPAT_MOUNTS="/folder1/":"/folder2/" %command%
```

Example:
If you install your instances on a secondary drive mounted at `/nvme2/`, under a folder called `/modding/`, the argument for you would be `STEAM_COMPAT_MOUNTS="/nvme2/modding" %command%`.

### Launching without opening MO2

You can pass a single parameter to Mod Organizer 2 through the game's launch options on Steam. This allows you to tell Mod Organizer 2 to skip its UI and directly launch an executable.

1. Open Steam;
2. Right click the game you want to launch directly and click on "Properties";
3. Scroll down to "Launch Options" within the "General" tab;
4. Write `'moshortcut://"executable name"'` in the launch options textbox. eg.:
   - `'moshortcut://"Fallout Launcher"'` will launch the original Fallout New Vegas launcher
   - `'moshortcut://"SKSE"'` will directly launch Skyrim and Skyrim SE, with SKSE enabled
5. Close the properties window and launch the game;

Example:
```bash
%command% 'moshortcut://"SKSE"'
```

**IMPORTANT:** Pay attention to the usage of single and double quotes in the examples above, as they ensure executable names including spaces will still work. The entire launch option should be wrapped in single quotes and the executable name should be wrapped in double quotes.

### 'gamemoderun' Issue
Usually, `gamemoderun` to a proton game's Launch Options within Steam can give a significant improvement in performance. </br>
However, it appears that having this option in a game that's been modified by this script will prevent MO2 from launching, rendering the game unplayable.

### Game Specific Adjustments

#### Cyberpunk 2077
Add the following to the game's Launch Options within Steam:</br>
```bash
WINEDLLOVERRIDES="winmm,version=n,b" %command%
```

## Alternative Proton Versions

**IMPORTANT:** Proton 9.0 is the most extensively tested version. The developer provides no guarantees that alternative versions will work well.
1. Close the game and Mod Organizer 2 if you have them open;
2. Select the Proton version you'd like to use on Steam and wait for it to execute any validations and updates;
3. Purge your existing game prefix to ensure a clean version transition:
	1. Open a file explorer or terminal of your choice;
	2. Navigate to "\<your steam library\>/steamapps/compatdata";
	3. Delete the folder named after the appid of the game - you can find all appids [here](gamesinfo);
4. Launch the game on Steam and let it run the first time setup;
5. (Optional\*) Run the installer again, select no when asked to update Mod Organizer 2;

\*Step 5 is for re-applying protontricks on the newly created prefix. Whether or not that is helpful depends on how well the Proton version you selected works out-of-the-box.

## Launching Mod Organizer 2 outside of Steam

**IMPORTANT:** Highly advised against. Steam runs Proton within its own special environment and Mod Organizer 2 may not properly utilize this environment when executed from outside of Steam. You can read [this reddit comment](https://www.reddit.com/r/linux_gaming/comments/k2kyjt/is_it_a_good_idea_to_use_proton_for_non_steam/gdxz70m/) where GloriousEggroll talks about this in more detail.

You can launch non-Steam applications with Proton using `protontricks-launch`.

Example:
```bash
WINEESYNC=1 WINEFSYNC=1 protontricks-launch --appid 489830 "$HOME/.config/modorganizer2/instances/skyrimspecialedition/modorganizer2/ModOrganizer.exe"
```

You can find the proper appid for the game you want [here](gamesinfo).

# Troubleshooting

Protontricks can randomly fail to apply the necessary overrides or configurations when called by a script. If you're having issues with the installer, try the following:
* Check the logs for any error messages or clues about what might be going wrong.
* Run the installer again and see if the issue persists.
* Try a different location for the Mod Organizer 2 location
* Make sure you have applied the necessary fixes listed in the above post-install documentation.
* If protontricks fails at a certain dependency, try installing it manually with their gui.
* If all else fails, check the [GitHub issues](https://github.com/Furglitch/modorganizer2-linux-installer/issues) for similar reports or to create a new issue.