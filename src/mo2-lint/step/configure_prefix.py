#!/usr/bin/env python3

from loguru import logger
from pathlib import Path

prompt_archive = """
It is highly recommended to clean your current game prefix before starting the installation process.
Would you like to archive your current game prefix and create a new one?
"""

prompt_clean_steam = """
In order to clean your game prefix, follow the instructions below:

1. Within Steam: right-click the game in your library, select 'Properties', and navigate to the 'Compatibility' tab.
2. Check the box for 'Force the use of a specific Steam Play compatibility tool' if it's not already checked.
   * Proton 9.0 is the currently supported and recommended version
3. From the dropdown menu, select your preferred Proton version.9.0 is the supported and recommended version.
4. Close the properties window and launch the game once to allow Steam to set up the new prefix.
5. Exit the game completely. Do not launch it until the installation process is finished.
"""

prompt_clean_heroic = """
In order to clean your game prefix, follow the instructions below:

1. Within Heroic: right-click the game in your library, select 'Settings', and navigate to the 'WINE' tab.
2. Under 'Wine Version', select your preferred Wine/Proton version.
   * Proton - Proton 9.0 (Beta) is the currently supported and recommended version.
     This is a stable release, not beta, but Valve never changed the file name.
   * If this version is not available, you will need to enable "Allow using Valve Proton builds to run games"
     in Heroic's Settings, under the 'Advanced' tab. Ensure that Proton 9.0 is then downloaded and installed in Steam.
3. Optional: Navigate to the 'OTHER' tab and check 'Use Steam Runtime'. This is recommended and may help with compatibility.
4. Launch the game once to allow Heroic to set up the new prefix.
5. Exit the game completely. Do not launch it until the installation process is finished.
"""

tricks = [
    "arial",
    "fontsmooth=rgb",
]


def configure():
    from util.variables import launcher, game_info

    global tricks
    tricks = tricks + game_info.get("protontricks_args", [])

    match launcher:
        case "steam":
            logger.info("Configuring Steam prefix")
            logger.info(
                "This may take a while. Failure at this step may indicate an issue with protontricks"
            )
            from util.wine import protontricks

            protontricks.apply(game_info["steam_id"], tricks)
        case "heroic":
            logger.info("Configuring Heroic prefix")
            logger.info(
                "This may take a while. Failure at this step may indicate an issue with winetricks"
            )
            from util.variables import heroic_config

            prefix = heroic_config[5]
            wine = heroic_config[4]
            if Path(wine).name == "proton":
                wine = Path(wine).parent / "files" / "bin" / "wine"
            logger.info(f'Using Heroic runner with wine: "{wine}", prefix: "{prefix}"')
            from util.wine import winetricks

            winetricks.apply(wine, prefix, tricks)


def main():
    configure()
