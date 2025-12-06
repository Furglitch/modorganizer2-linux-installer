#!/usr/bin/env python3

import click
from pathlib import Path
from loguru import logger

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


def internal_file(*parts):
    import sys

    path = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve()))
    return path.joinpath(*parts)


@click.command()
@click.version_option(version="1.0.0", prog_name="mo2-lint")
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

    logger.debug(f"Received URL: {url}")
    if url.startswith("nxm://"):
        game_id = url[len("nxm://") :].split("/", 1)[0]
        logger.debug(f"Parsed game ID: {game_id}")
    else:
        logger.warning("Invalid NXM URL format.")
        return

    instance_link = Path(f"~/.config/mo2-lint/instances/{game_id}").expanduser()
    instance_dir = instance_link.resolve()
    if not instance_dir.exists():
        if instance_link.is_symlink():
            instance_link.unlink()
            pass
        logger.warning(f"Instance directory does not exist: {instance_dir}")
        return

    env_file = Path(instance_dir / "lint.env")
    logger.debug(f"Looking for env file at: {env_file}")
    if env_file.exists():
        from dotenv import dotenv_values

        info = dotenv_values(env_file)
        logger.trace(f"Loaded env file: {info}")
        global launcher, steam_id, gog_id, epic_id
        for key, value in info.items():
            if str(key) == "launcher":
                launcher = str(value)
            if str(key) == "steam_id":
                steam_id = int(value)
            if str(key) == "gog_id":
                gog_id = int(value)
            if str(key) == "epic_id":
                epic_id = str(value)
        logger.debug(
            f"Set launcher to {launcher}, steam_id to {steam_id}, gog_id to {gog_id}, epic_id to {epic_id}"
        )
        match launcher:
            case "steam":
                logger.info("Using steam launcher handler.")
                pass
            case "heroic":
                logger.info("Using heroic launcher handler.")
                finder = internal_file("dist", "find_heroic_install")
                import subprocess

                proc = subprocess.run(
                    [finder, "--gog-id", f"{gog_id}", "--epic-id", f"{epic_id}"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                logger.trace(f"Heroic finder stdout: {proc.stdout!r}")
                out = (proc.stdout)[proc.stdout.find("{") : proc.stdout.rfind("}") + 1]
                logger.trace(f"Received from heroic finder: {out!r}")
                import ast

                json = ast.literal_eval(out)
                logger.trace(f"Heroic finder output JSON: {json}")
                wine = str(json.get("wine"))
                release = str(json.get("release"))
                app = str(json.get("id"))
                runner = str(json.get("launcher"))

                if Path(wine).name == "proton":
                    wine = Path(wine).parent / "files" / "bin" / "wine"
                else:
                    wine = Path(wine)
                logger.debug(f"Resolved heroic wine path: {wine}")

    exe = ("Z:" + str(instance_dir) + "/ModOrganizer.exe").replace("/", "\\")
    logger.debug(f"Resolved instance directory: {exe}")
    import subprocess
    import psutil

    found = False
    logger.info("Checking for running Mod Organizer 2 instances...")
    for p in psutil.process_iter():
        cmdline = p.cmdline()
        for c in cmdline:
            cmd = c.strip('"').strip("'")
            if exe in cmd:
                found = True
                break
        if found:
            break
    if found:
        logger.debug("Found running Mod Organizer 2 instance.")
    elif not found:
        logger.debug("No running Mod Organizer 2 instance found.")
        logger.info(f"Starting Mod Organizer 2 to download {url}")
        match launcher:
            case "steam":
                cmd = ["steam", "-applaunch", f"{steam_id}", f"{url}"]
                logger.trace(f"Launching via Steam: {cmd}")
                subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                )
            case "heroic":
                cmd = (
                    "heroic://launch"
                    + f"?appName={app}"
                    + f"&launcher={runner}"
                    + f"&arg={url}"
                )
                cmd = ["xdg-open", cmd]
                logger.trace(f"Launching via Heroic: {cmd}")
                subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                )
                pass

    logger.info(f"Sending download {url} to running Mod Organizer 2 instance.")
    handler = instance_dir / "nxmhandler.exe"
    import os

    env = os.environ.copy()
    env.setdefault("WINEESYNC", "1")
    env.setdefault("WINEFSYNC", "1")
    match launcher:
        case "steam":
            cmd = [
                "protontricks-launch",
                "--appid",
                f"{steam_id}",
                f"{handler}",
                f"{url}",
            ]
        case "heroic":
            match release:
                case "stable":
                    cmd = [f"{wine}", f"{handler}", f"{url}"]
                case "flatpak":
                    cmd = [
                        "flatpak",
                        "run",
                        f"--command='{wine}'",
                        "com.heroicgameslauncher.hgl",
                        f"{handler}",
                        f"{url}",
                    ]

    logger.trace(f"Executing handler command: {cmd}")
    subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env
    )


if __name__ == "__main__":
    main()
