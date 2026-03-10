#!/usr/bin/env python3

from loguru import logger
from pathlib import Path
from typing import Optional
from shared.logger import add_loggers, remove_loggers
import protontricks_util as protontricks
import state_file as state
import click
import os
import psutil
import subprocess

version = "3.0.0"


def get_instance_dir(url: str) -> Optional[Path]:
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


def get_env(instance_dir: Path) -> dict:
    state.load_state()
    instance = state.check_existing_instances(str(instance_dir))
    info = state.game_data(instance)

    # Initialize with defaults
    launcher = info.get("launcher", "")
    steam_id = int(info.get("steam_id")) if info.get("steam_id") else None
    gog_id = int(info.get("gog_id")) if info.get("gog_id") else None
    epic_id = info.get("epic_id", "")

    logger.debug(
        f"Loaded instance data - launcher: {launcher}, steam_id: {steam_id}, gog_id: {gog_id}, epic_id: {epic_id}"
    )

    release, runner, app, wine, prefix = None, None, None, None, None

    if launcher in ["heroic", "gog", "epic"]:
        logger.info("Using heroic launcher handler.")
        from find_heroic_install import get_heroic_data

        use_gog_id = gog_id if gog_id and (not epic_id or gog_id) else None
        use_epic_id = epic_id if epic_id and not use_gog_id else None

        # get_heroic_data returns: (release, launcher, app_id, wine_path, wine_prefix)
        release, runner, app, wine, prefix = get_heroic_data(use_gog_id, use_epic_id)

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


def check_instance(instance_dir: Path) -> bool:
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


def launch_instance(
    launcher: str,
    steam_id: Optional[int],
    url: str,
    runner: Optional[str] = None,
    app: Optional[str] = None,
) -> None:
    logger.info(f"Starting Mod Organizer 2 to download {url}")
    if launcher == "steam":
        cmd = ["steam", "-applaunch", f"{steam_id}", f"{url}"]
        logger.trace(f"Launching via Steam: {cmd}")
        subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    elif launcher in ["heroic", "gog", "epic"]:
        cmd = (
            "heroic://launch"
            + f"?appName={app}"
            + f"&launcher={runner}"
            + f"&arg={url}"
        )
        cmd = ["xdg-open", cmd]
        logger.trace(f"Launching via Heroic: {cmd}")
        subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def send_url(instance_dir: Path, url: str, env_info: dict) -> None:
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
        cmd = f"wine '{handler}' '{url}'"
        protontricks.run(["-c", cmd, str(steam_id)])
    elif launcher in ["heroic", "gog", "epic"]:
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
@click.version_option(version=version, prog_name="mo2-lint-nxm-handler")
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
def main(url: str, log_level: str) -> None:
    """A handler for Nexus Mods URLs to interact with Mod Organizer 2 instances that are managed by mo2-lint. (Enables the 'Mod Manager Download' button on mod pages.)"""
    remove_loggers()
    add_loggers(
        log_level=log_level.upper(), script="nxm-handler", process="nxm-handler"
    )

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
