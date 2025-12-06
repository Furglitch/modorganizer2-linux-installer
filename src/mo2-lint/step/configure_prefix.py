#!/usr/bin/env python3

from loguru import logger
from pathlib import Path

prompt_archive = """It is highly recommended to clean your current game prefix before starting the installation process.
"""

prompt_clean_steam = """In order to create a clean game prefix, follow the instructions below:

1. In Steam: right-click the game in your library, select 'Properties', and navigate to the 'Compatibility' tab.
2. Check the box for 'Force the use of a specific Steam Play compatibility tool' if it's not already checked.
   * Proton 9.0 is the currently supported and recommended version
3. From the dropdown menu, select your preferred Proton version. 9.0 is the supported and recommended version.
4. Close the properties window and launch the game once to allow Steam to set up the new prefix.
5. Exit the game completely. Do not launch it until the installation process is finished.
"""

prompt_clean_heroic = """In order to create a clean game prefix, follow the instructions below:

1. In Heroic: right-click the game in your library, select 'Settings', and navigate to the 'WINE' tab.
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


def archive_prefix(prefix: str = None):
    import util.variables as var

    if Path(prefix.strip()).exists():
        prefix_path = Path(prefix.strip())
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        var.archived_prefix = prefix_path.with_name(f"{prefix_path.name}.{timestamp}")
        try:
            import shutil

            shutil.move(str(prefix_path), str(var.archived_prefix))
            logger.debug(f"Archived prefix to {var.archived_prefix}")
        except Exception as e:
            logger.error("Failed to archive existing prefix. See debug for details.")
            logger.debug(f"Exception: {e}")
            raise


def restore_prefix_data(prefix: str = None):
    from util.variables import launcher, archived_prefix

    match launcher:
        case "steam":
            src = Path(archived_prefix) / "pfx" / "drive_c" / "users"
        case "heroic":
            src = Path(archived_prefix) / "drive_c" / "users"
    dst = Path(prefix) / "drive_c" / "users"
    try:
        import shutil

        shutil.move(str(dst), str(dst) + ".bak")
        shutil.move(str(src), str(dst))
        logger.debug(f"Restored archived prefix from {archived_prefix}")
    except Exception as e:
        logger.error("Failed to restore archived prefix. See debug for details.")
        logger.debug(f"Exception: {e}")


def create_prefix() -> bool:
    from util.variables import launcher

    match launcher:
        case "steam":
            logger.debug("Prompting user to clean Steam prefix")
            print(prompt_clean_steam)
        case "heroic":
            logger.debug("Prompting user to clean Heroic prefix")
            print(prompt_clean_heroic)
    if input("Have you completed these instructions? [y/N]: ").strip().lower() in (
        "",
        "y",
        "yes",
    ):
        return True
    else:
        return False


def load_prefix():
    from util.variables import launcher, game_info

    match launcher:
        case "steam":
            from util.wine import protontricks

            prefix = protontricks.get_prefix(game_info["steam_id"])
        case "heroic":
            from util.variables import heroic_config

            prefix = heroic_config[5]
        case _:
            prefix = None
    return prefix


def prompt_prefix():
    prefix = load_prefix()
    if prefix is not None and Path(prefix.strip()).exists():
        logger.debug(f"Using existing prefix at {prefix}")
    else:
        if prefix is None:
            logger.error("Was unable to determine prefix path.")
        elif not Path(prefix.strip()).exists():
            logger.warning(f"Prefix path does not exist: {prefix.strip()}")
        logger.warning("Make sure you have run the game at least once.")
        raise SystemExit(1)
    logger.debug("Prompting user to archive existing prefix")
    print(prompt_archive)
    if input(
        "Would you like to archive your current game prefix and create a new one? [y/N]: "
    ).strip().lower() in (
        "",
        "y",
        "yes",
    ):
        from util.variables import launcher

        _prefix = (
            str(Path(prefix).expanduser())
            if launcher != "steam"
            else str(Path(prefix).parent.expanduser())
        )
        archive_prefix(_prefix)
    else:
        logger.debug("User refused to archive the prefix.")
    if create_prefix() is True:
        logger.debug("User confirmed prefix cleaning.")
    else:
        logger.critical("Aborting operation...")
        raise SystemExit(1)
    from util.variables import archived_prefix

    logger.debug(f"Archived prefix: {archived_prefix}")
    if archived_prefix is not None:
        logger.debug("Restoring personal data from archived prefix.")
        restore_prefix_data(prefix)
        info = """Your own prefix has been archived and a new clean prefix has been created.
You can find your archived prefix at: {archived_prefix}

Personal data from the archived prefix (e.g. saved games) has been preserved and restored to the new prefix.
Feel free to delete the archive if you no longer need it after confirming your data is intact.

A list of all archived prefixes can be found at: TBD""".format(
            archived_prefix=archived_prefix
        )
        print(info)


def configure():
    from util.variables import launcher, game_info

    global tricks
    tricks = tricks + game_info.get("protontricks_args", [])

    match launcher:
        case "steam":
            logger.info("Configuring Steam prefix with protontricks")
            logger.info(
                "This may take a while. Failure at this step may indicate an issue with protontricks"
            )
            from util.wine import protontricks

            protontricks.apply(game_info["steam_id"], tricks)
        case "heroic":
            logger.info("Configuring Heroic prefix with winetricks")
            logger.info(
                "This may take a while. Failure at this step may indicate an issue with winetricks"
            )
            from util.variables import heroic_config

            prefix = heroic_config[5]
            wine = heroic_config[4]
            if Path(wine).name == "proton":
                wine = Path(wine).parent / "files" / "bin" / "wine"
            logger.debug(f'Using Heroic runner with wine: "{wine}", prefix: "{prefix}"')
            from util.wine import winetricks
            from step.external_resources import download_resources

            download_resources()
            winetricks.apply(wine, prefix, tricks)


def main():
    prompt_prefix()
    try:
        configure()
    except Exception as e:
        logger.error(
            "An error occurred while configuring the prefix. See debug for details."
        )
        logger.debug(f"Exception: {e}")
        import traceback

        logger.debug("Traceback:\n" + traceback.format_exc())
        if input(
            "Would you like to ignore and continue? [y/N]: "
        ).strip().lower() not in ("", "y", "yes"):
            logger.critical("Aborting operation...")
            raise SystemExit(1)
