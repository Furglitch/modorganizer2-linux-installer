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
            print(f"Key: {key}, Value: {value}")
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
                out = (proc.stdout)[proc.stdout.find("{") : proc.stdout.rfind("}") + 1]
                logger.trace(f"Received from heroic finder: {out!r}")

                import ast

                json = ast.literal_eval(out)
                wine = str(json.get("wine"))

                if Path(wine).name == "proton":
                    wine = Path(wine).parent / "files" / "bin" / "wine"
                else:
                    wine = Path(wine)
                logger.debug(f"Resolved heroic wine path: {wine}")

    exe = ("Z:" + str(instance_dir) + "/ModOrganizer.exe").replace("/", "\\\\")
    logger.debug(f"Resolved instance directory: {exe}")
    import subprocess
    import shutil

    pgrep = shutil.which("pgrep") or "pgrep"
    cmd = [pgrep, "-f", exe]
    logger.debug(f"Running command: {' '.join(cmd)}")
    proc = subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    logger.debug("Running pgrep")
    if proc.stdout:
        logger.debug("Successful pgrep for Mod Organizer 2 instance.")
        # TODO if [ "$process_search_status" == "1" ]; then
    else:
        logger.error(
            f"Application not running: {exe.replace('Z:', '').replace('\\\\', '/')}"
        )
        # TODO if [ "$process_search_status" != "1" ]; then
        return

    # TODO if [ "$download_start_status" != "0" ]; then


if __name__ == "__main__":
    main()
