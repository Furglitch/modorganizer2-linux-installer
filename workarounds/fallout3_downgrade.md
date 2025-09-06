# Downgrading Fallout 3

Fallout 3 released an anniversary update in 2024, but the majority of the modding community have decided to stick with the 2021 version.
As such, this script will set up MO2 for the pre-anniversary version of Fallout 3 and GOTY. The script will fail if you are on the Anniversary update.

**If you still with to install MO2 for the anniversary update:** Go to [/gamesinfo/fallout3.sh](../gamesinfo/fallout3_goty.sh) or [/gamesinfo/fallout3.sh](../gamesinfo/fallout3_goty.sh) and change `game_executable=` to `game_executable="Fallout3Launcher.exe"`, then run the script.

## Instructions for Downgrading

1. Open your terminal and run `xdg-open steam://open/console`. In your steam client, a previously hidden 'Console' tab should open.
2. In the console, run the following command: 
   Fallout 3: `download_depot 22300 22301 7414504515121985658`
   Fallout 3 GOTY: `download_depot 22370 22371 4929549459338680299`
3. Once the download finishes, it will give you a directory path. Follow that directory path into the `depot_22301`/`depot_22371` folder
4. Inside the folder, there will be many files, including `FalloutLauncherSteam.exe`. Copy ALL the files into your Fallout 3 installation.
5. Run the game once to confirm there are no corrupted files. After that, you can run the installer script again.