#!usr/bin/env python3

from pathlib import Path

from loguru import logger
from step.configure_prefix import prompt as configure_prefix
from step.external_resources import download, download_winetricks
from step.launch_opt import add_launch_opt
from step.load_game_info import get_launcher, get_library
from step.workarounds import apply_workarounds
from util import state_file as state
from util import variables as var
from util.nexus.install_handler import install as install_handler
from util.redirector.install import install as install_redirector
from util.state_file import InstanceData, set_index
from util.steam.proton_wrapper import resolve as resolve_proton_wrapper
from util.lang import post_install_steam, post_install_heroic


def get_install_dir(
    game: str,
    directory: Path | None,
    launcher: str | None,
) -> Path | None:
    if directory:
        return Path(directory).expanduser().resolve()

    if not var.settings or not var.settings.root_folder:
        return None

    root_folder = var.settings.root_folder.expanduser().resolve()
    folder_name = var.settings.folder_name
    if not folder_name:
        return root_folder

    resolved_launcher = launcher or var.settings.launcher
    if "{launcher}" in folder_name and not resolved_launcher:
        resolved_launcher = get_launcher()
    if "{launcher}" in folder_name and not resolved_launcher:
        logger.critical(
            "folder_name uses the {launcher} placeholder, but no launcher could be determined."
        )
        raise SystemExit(1)

    try:
        rendered_folder_name = folder_name.format(
            game=game,
            launcher=resolved_launcher or "",
        )
    except KeyError as error:
        logger.critical(f"Unknown folder_name placeholder: {error.args[0]}")
        raise SystemExit(1)
    if not rendered_folder_name:
        return root_folder

    return root_folder / rendered_folder_name


def install(
    game: str,
    directory: Path | None,
    game_info_path: Path | None = None,
    log_level: str = "INFO",
    script_extender: bool = False,
    plugin: tuple[str] | None = (),
    theme: str | None = None,
    launcher: str | None = None,
    proton_version: str | None = None,
    mo2_archive: Path | None = None,
    mo2_checksum: str | None = None,
):
    directory = get_install_dir(game, directory, launcher)
    var.set_parameters(
        {
            "game": game,
            "directory": directory,
            "game_info_path": game_info_path,
            "log_level": log_level,
            "script_extender": script_extender,
            "theme": theme,
            "plugins": list(plugin),
            "mo2_archive": mo2_archive,
            "mo2_checksum": mo2_checksum,
        }
    )
    logger.debug(f"Starting installation with parameters: {var.input_params}")

    directory.mkdir(parents=True, exist_ok=True)
    logger.debug(f"Ensured installation directory exists: {directory}")

    if not state.match_instances(directory=directory):
        launcher = get_launcher(launcher)

        executable = (
            var.game_info.executable.get(launcher)
            if isinstance(var.game_info.executable, dict)
            else var.game_info.executable
        )

        game_path = get_library()
        if game_path is None:
            logger.critical(
                "Could not determine the game installation path. Aborting installation before modifying the instance."
            )
            raise SystemExit(1)

        proton_wrapper = None
        if launcher == "steam":
            appid = var.game_info.launcher_ids.steam
            proton_wrapper = resolve_proton_wrapper(appid, proton_version)

            if not proton_wrapper:
                logger.critical(
                    "Could not resolve Steam Proton wrapper. Aborting installation because MO2 will not launch through Steam without the Proton wrapper."
                )
                raise SystemExit(1)

            if proton_version:
                proton_wrapper.pinned = True

        state.current_instance = InstanceData(
            index=-1,
            game=game,
            nexus_slug=var.game_info.nexus_slug,
            instance_path=directory,
            pin=mo2_archive is not None,
            launcher=launcher,
            launcher_ids=var.LauncherIDs.from_dict(var.game_info.launcher_ids),
            game_path=game_path,
            game_executable=executable,
            proton_wrapper=proton_wrapper,
            script_extender=None,
            plugins=list(plugin),
        )
        set_index()
    else:
        logger.critical(
            "An instance with the specified directory already exists. Aborting installation to prevent conflicts."
        )
        logger.warning(
            "Please choose a different installation directory or uninstall the existing instance before proceeding."
        )
        raise SystemExit(1)

    download_winetricks()
    configure_prefix()
    logger.info("Prefix configuration completed")

    download()
    logger.info("Download phase completed")

    install_handler()
    logger.info("Installation handler completed")

    install_redirector()
    logger.info("Redirector installation completed")

    add_launch_opt()
    logger.info("Launch method configured")

    apply_workarounds()
    logger.info("Workarounds applied")
    logger.success("Installation completed successfully")

    display_name = var.game_info.display_name
    if launcher == "steam":
        print(post_install_steam.format(game=display_name))
    elif launcher in ["gog", "epic"]:
        print(post_install_heroic)
