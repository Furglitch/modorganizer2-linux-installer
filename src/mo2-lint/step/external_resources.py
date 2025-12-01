#!/usr/bin/env python3

from pathlib import Path
from loguru import logger

name: dict[str, str] = {}
url: dict[str, str] = {}
nexus_id: dict[str, tuple[int, int]] = {}
checksum: dict[str, str] = {}
files: dict[str, list] = {}
download_dir: dict[str, Path] = {}
extract_dir: dict[str, Path] = {}
cache_dir: Path = Path("~/.cache/mo2-lint").expanduser()


def download_scriptextender():
    import util.variables as var

    if var.launcher == "heroic":
        info = var.game_info.get("script_extender", {}).get(var.heroic_runner, {})
    else:
        info = var.game_info.get("script_extender", {}).get("steam", {})

    se = "scriptextender"
    se_info = info.get("resource", {})
    name[se] = "Script Extender"
    url[se] = se_info.get("url")
    nexus_id[se] = se_info.get("mod_id"), se_info.get("file_id")
    checksum[se] = se_info.get("checksum")
    files[se] = info.get("files")

    logger.trace(
        f"Determined values for Script Extender: URL={url.get(se)}, Nexus IDs={nexus_id.get(se)}, Checksum={checksum.get(se)}, Files={files.get(se)}"
    )
    get_paths(se)
    download(se)
    extract(se)
    install(se)


def download_resources():
    from util.variables import load_resourceinfo

    load_resourceinfo()
    from util.variables import parameters, resource_info as info

    for resource in (
        ("mod_organizer", "winetricks", "java")
        if parameters.get("game") == ("skyrim" or "enderal")
        else ("mod_organizer", "winetricks")
    ):
        name[resource] = resource.replace("_", " ").title()
        url[resource] = info.get(resource, {}).get("download_url")
        checksum[resource] = info.get(resource, {}).get("checksum")
        files[resource] = ["*"]
        get_paths(resource)
        download(resource)
        if not resource == "winetricks":
            extract(resource)
            install(resource)


def download_plugins(plugin: str):
    from util.variables import load_plugininfo

    info = load_plugininfo()
    manifest = {}
    for entry in info:
        if entry.get("Identifier") == plugin:
            manifest[plugin] = entry.get("Manifest")
            break

    from urllib.request import urlretrieve as dl

    file = Path(dl(manifest.get(plugin))[0])
    with open(file, "r") as f:
        from pydantic_core import from_json

        json = from_json(f.read())
        logger.trace(f"Downloaded plugin manifest for {plugin}: {json}")

    name[plugin] = json.get("Name")
    latest = json.get("Versions", [])[-1]
    files[plugin] = latest.get("PluginPath")
    url[plugin] = latest.get("DownloadUrl")
    checksum[plugin] = None

    get_paths(plugin)
    download(plugin)
    extract(plugin)
    install(plugin)


def check_existing(src: str, dir: Path) -> bool:
    match src:
        case "mod_organizer":
            return (dir / "ModOrganizer.exe").exists()
        case "winetricks":
            return (dir / "winetricks").exists()
        case "java":
            return (dir / "bin" / "java").exists()
        case "scriptextender":
            return any((dir / f).exists() for f in files.get(src, []))


def get_paths(src: str):
    filename = url.get(src).split("/")[-1]

    download_dir[src] = cache_dir / "downloads" / filename
    download_dir.get(src).parent.mkdir(parents=True, exist_ok=True)
    logger.debug(f"Download path for {src}: {download_dir.get(src)}")

    extract_dir[src] = cache_dir / "extracted" / Path(filename).stem
    extract_dir.get(src).mkdir(parents=True, exist_ok=True)
    logger.debug(f"Extraction path for {src}: {extract_dir.get(src)}")


def download(src: str):
    from util.checksum import checksum_local

    hash = checksum.get(src) if checksum.get(src) else None
    dir = download_dir.get(src)

    if hash is not None and dir.exists():
        logger.debug(f"{src} already downloaded at {dir}; ensuring validity.")
        if checksum_local(dir, hash):
            logger.debug(f"Checksum for {src} verified.")
            if src == "winetricks":
                import stat

                dir.chmod(dir.stat().st_mode | stat.S_IEXEC)
            return

    _name = name.get(src)
    _url = url.get(src)
    attempts = 3
    for i in range(attempts):
        logger.trace(f"Attempt {i + 1} to download {_name} from {_url}")
        from urllib.request import urlretrieve as dl

        try:
            dl(_url, dir)
            checksum_local(dir, hash)
            logger.debug(f"Downloaded {_name} to {dir} and verified checksum.")
            if src == "winetricks":
                import stat

                dir.chmod(dir.stat().st_mode | stat.S_IEXEC)
            return
        except Exception as e:
            logger.error(f"Failed to download {_name} on attempt {i + 1}: {e}")
    logger.error(f"Failed to download resource after {attempts} attempts.")


def extract(src: str):
    if not check_existing(src, extract_dir.get(src)):
        try:
            from patoolib import extract_archive as unzip

            unzip(str(download_dir.get(src)), outdir=extract_dir.get(src))
            logger.debug(f"Extracted {name.get(src)} to {extract_dir.get(src)}")
        except Exception as e:
            logger.error(f"Failed to extract {name.get(src)}: {e}")


def install(src: str):
    _name = name.get(src)
    dir = None
    from util.variables import parameters

    match src:
        case "mod_organizer":
            dir = Path(parameters.get("directory")).expanduser()
        case "java":
            from util.variables import prefix

            dir = Path(prefix) / "drive_c" / "java".expanduser()
        case "scriptextender":
            from util.variables import game_install_path

            dir = Path(game_install_path).expanduser()
        case src if src in (parameters.get("plugins")):
            dir = (Path(parameters.get("directory")) / "plugins").expanduser()
    dir.mkdir(parents=True, exist_ok=True)

    if check_existing(src, dir):
        logger.debug(f"{_name} already installed at {dir}; skipping installation.")
        return
    else:
        try:
            from shutil import copytree, copy2

            if (
                files[src] != "*"
                and files[src] != ["*"]
                and files[src] != []
                and files[src] is not None
            ):
                for file in files[src]:
                    file = Path(file)
                    source = extract_dir.get(src) / file
                    destination = dir / file.name
                    if not source.exists():
                        logger.warning(
                            f"Expected file {source} does not exist; aborting installation."
                        )
                        return
                    elif source.is_dir():
                        copytree(source, destination, dirs_exist_ok=True)
                        logger.trace(f"Copied directory {source} to {destination}.")
                    elif source.is_file() and not destination.exists():
                        copy2(source, destination)
                        logger.trace(f"Copied file {source} to {destination}.")
                    else:
                        logger.warning(
                            f"Destination {destination} already exists; skipping copy of {source}."
                        )
            else:
                copytree(extract_dir.get(src), dir, dirs_exist_ok=True)
        except Exception as e:
            import traceback

            logger.error(f"Failed to install {_name}: {e}")
            logger.debug("Traceback:\n" + traceback.format_exc())
    logger.success(f"Installed {_name} to {dir}.")


def symlink_instance():
    from pathlib import Path
    from util.variables import parameters, game_info

    source = Path(parameters.get("directory")).expanduser()
    target = Path("~/.config/mo2-lint/instances").expanduser()
    target.mkdir(parents=True, exist_ok=True)
    link = target / game_info.get("nexus_id")

    if not source.exists():
        logger.warning(f"MO2 instance directory does not exist: {source}")
        return
    try:
        if link.exists() or link.is_symlink():
            if link.is_symlink() and link.resolve() == source.resolve():
                logger.debug(f"Symlink already correct at {link}")
                return
            elif link.is_symlink():
                link.unlink()
                logger.debug(f"Removed stale symlink at {link}")
            else:
                logger.warning(
                    f"Path exists, but is not a symlink. Please remove it manually: {link}"
                )
                return
        link.symlink_to(source)
        logger.success(f"Created symlink {link} -> {source}")
    except Exception as e:
        logger.error(f"Failed to create symlink {link} -> {source}: {e}")


def main():
    cache_dir.mkdir(parents=True, exist_ok=True)
    logger.debug(f"Cache directory ensured at {cache_dir}")
    from util.variables import parameters, game_info, launcher

    if (
        parameters.get("script_extender") is True
        and game_info.get("script_extender").get(launcher) is not None
    ):
        download_scriptextender()
    download_resources()
    if parameters.get("plugins"):
        for plugin in parameters.get("plugins"):
            download_plugins(plugin)
    symlink_instance()
