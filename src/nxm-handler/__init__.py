#!/usr/bin/env python3

import click
from pathlib import Path
from loguru import logger
import state_file as state
import subprocess
import psutil
import os

stdout = None
logout = None

launcher: str = None
steam_id: int = None
gog_id: int = None
epic_id: str = None


def set_logger(log_level):
    import sys

    global stdout, logout

    logger.remove(stdout)
    logger.remove(logout)

    stdout = logger.add(
        sys.stdout,
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <bold>NXM Handler</bold> | {message}",
        level=log_level,
    )

    filename = Path(
        "~/.cache/mo2-lint/logs/nxm-handler.{time:YYYY-MM-DD_HH-mm-ss}.log"
    ).expanduser()
    logout = logger.add(
        filename,
        level="TRACE",
        rotation="10 MB",
        retention="7 days",
        compression="zip",
    )


def get_instance_dir(url):
    logger.debug(f"Received URL: {url}")
    if not url.startswith("nxm://"):
        logger.warning("Invalid NXM URL format.")
        return None

    game_id = url[len("nxm://") :].split("/", 1)[0]
    logger.debug(f"Parsed game ID: {game_id}")

    instance_link = Path(f"~/.config/mo2-lint/instances/{game_id}").expanduser()
    instance_dir = instance_link.resolve()
    if not instance_dir.exists():
        if instance_link.is_symlink():
            try:
                instance_link.unlink()
            except Exception:
                logger.exception("Failed to remove broken symlink")
        logger.warning(f"Instance directory does not exist: {instance_dir}")
        return None

    return instance_dir


def get_env(instance_dir):
    state.load_state()
    instance = state.check_existing_instances(str(instance_dir))
    info = state.game_data(instance)

    for key, value in info.items():
        if str(key) == "launcher":
            logger.debug(f"Setting launcher to {value}")
            launcher = str(value)
        if str(key) == "steam_id" and value is not None and value != "":
            logger.debug(f"Setting steam_id to {value}")
            steam_id = int(value)
        if str(key) == "gog_id" and value is not None and value != "":
            logger.debug(f"Setting gog_id to {value}")
            gog_id = int(value)
        if str(key) == "epic_id":
            logger.debug(f"Setting epic_id to {value}")
            epic_id = str(value)

    logger.debug(
        f"Set launcher to {launcher}, steam_id to {steam_id}, gog_id to {gog_id}, epic_id to {epic_id}"
    )

    release, runner, app, wine, prefix = None, None, None, None, None

    if launcher == "heroic":
        logger.info("Using heroic launcher handler.")
        from find_heroic_install import get_heroic_data

        release, runner, app, wine, prefix = get_heroic_data(gog_id, epic_id)

        if wine is None:
            logger.warning(
                "Heroic handler did not return a wine path; continuing without resolved wine path"
            )
        else:
            try:
                if Path(wine).name == "proton":
                    wine = Path(wine).parent / "files" / "bin" / "wine"
                else:
                    wine = Path(wine)
            except Exception:
                logger.exception("Failed to resolve heroic wine path")
                wine = None
    elif launcher == "steam":
        logger.info("Using steam launcher handler.")

    return {
        "launcher": launcher,
        "steam_id": steam_id,
        "gog_id": gog_id,
        "epic_id": epic_id,
        "release": release,
        "runner": runner,
        "app": app,
        "wine": wine,
        "prefix": prefix,
    }


def check_instance(instance_dir):
    exe = ("Z:" + str(instance_dir) + "/ModOrganizer.exe").replace("/", "\\")
    logger.debug(f"Resolved instance directory: {exe}")

    found = False
    logger.info("Checking for running Mod Organizer 2 instances...")
    for p in psutil.process_iter():
        try:
            cmdline = p.cmdline()
        except Exception:
            continue
        for c in cmdline:
            cmd = c.strip('"').strip("'")
            if exe in cmd:
                found = True
                break
        if found:
            break

    if found:
        logger.debug("Found running Mod Organizer 2 instance.")
    else:
        logger.debug("No running Mod Organizer 2 instance found.")

    return found


def launch_instance(launcher, steam_id, url, runner=None, app=None):
    logger.info(f"Starting Mod Organizer 2 to download {url}")
    if launcher == "steam":
        cmd = ["steam", "-applaunch", f"{steam_id}", f"{url}"]
        logger.trace(f"Launching via Steam: {cmd}")
        subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    elif launcher == "heroic":
        cmd = (
            "heroic://launch"
            + f"?appName={app}"
            + f"&launcher={runner}"
            + f"&arg={url}"
        )
        cmd = ["xdg-open", cmd]
        logger.trace(f"Launching via Heroic: {cmd}")
        subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def send_url(instance_dir, url, env_info):
    logger.info(f"Sending download {url} to running Mod Organizer 2 instance.")
    handler = instance_dir / "nxmhandler.exe"

    env = os.environ.copy()
    env.setdefault("WINEESYNC", "1")
    env.setdefault("WINEFSYNC", "1")

    launcher = env_info.get("launcher")
    steam_id = env_info.get("steam_id")
    release = env_info.get("release")
    wine = env_info.get("wine")
    prefix = env_info.get("prefix")

    if launcher == "steam":
        from protontricks.cli.main import main as pt

        pt("--verbose", "--appid", f"{steam_id}", f"{handler}", f"{url}")
    elif launcher == "heroic":
        if release == "stable":
            cmd = [f"{wine}", f"{handler}", f"{url}"]
            env.setdefault("WINEPREFIX", f"{prefix}")
        else:
            cmd = [
                "flatpak",
                "run",
                f"--command='{wine}'",
                "com.heroicgameslauncher.hgl",
                f"{handler}",
                f"{url}",
            ]
        try:
            subprocess.run(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env
            )
            logger.debug(f"Executing handler command: {cmd}")
        except Exception as e:
            logger.exception(f"Failed to execute handler command: {e}")
    else:
        logger.warning("Unknown launcher, cannot send URL")
        return


@click.command()
@click.version_option(version="2.0.0", prog_name="mo2-lint-nxm-handler")
@click.help_option("-h", "--help")
@click.argument(
    "url",
    type=str,
    required=True,
)
@click.option(
    "--log-level",
    "-l",
    type=click.Choice(["DEBUG", "INFO", "TRACE"], case_sensitive=False),
    default="INFO",
    help="Set the logging level.",
    show_default=True,
)
def main(url, log_level):
    """A handler for Nexus Mods URLs to interact with Mod Organizer 2 instances that are managed by mo2-lint. (Enables the 'Mod Manager Download' button on mod pages.)"""
    set_logger(log_level.upper())

    instance_dir = get_instance_dir(url)
    if not instance_dir:
        return

    env_info = get_env(instance_dir)
    found = check_instance(instance_dir)
    if not found:
        launch_instance(
            env_info.get("launcher"),
            env_info.get("steam_id"),
            url,
            env_info.get("runner"),
            env_info.get("app"),
        )
    send_url(instance_dir, url, env_info)


if __name__ == "__main__":
    main()
