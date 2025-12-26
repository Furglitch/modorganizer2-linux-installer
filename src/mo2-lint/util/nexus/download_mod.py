#!/usr/bin/env python3

from loguru import logger
from pathlib import Path
from ..state import state_file as state
import json


def get_api_key() -> str:
    state_file = state.state_file
    with state_file.open("r", encoding="utf-8") as f:
        state_data = json.load(f)
        api_key = state_data.get("nexus_api", {}).get("api_key", "")
    if not api_key:
        logger.warning("Nexus API key not found in state file.")
        from .api import main as nexus_key

        api_key = nexus_key()
        if not api_key:
            logger.error("Failed to obtain Nexus API key.")
            raise Exception("Nexus API key is required but could not be obtained.")
    else:
        logger.trace(f"Loaded existing Nexus API key: {api_key}")
    return api_key


def header() -> dict:
    api_key = get_api_key()
    from ..variables import version

    header = {
        "apikey": f"{api_key}",
        "Application-Name": "mo2lint",
        "Application-Version": version,
    }
    logger.trace(f"Constructed request header: {header}")
    return header


def nexus_request(url: str):
    import requests

    headers = header()
    response = requests.get(url, headers=headers)
    return response


def filename(game_id: str, mod_id: str, file_id: str) -> str:
    url = f"https://api.nexusmods.com/v1/games/{game_id}/mods/{mod_id}/files/{file_id}.json"
    file = nexus_request(url)
    json = file.json()
    name = json.get("file_name", "")
    logger.trace(
        f"Retrieved filename: {name} for game: {game_id}, mod: {mod_id}, file: {file_id}"
    )
    return name


def nexus_download(
    game_id: str, mod_id: str, file_id: str, dest: Path, file: str = None
):
    import requests

    url = f"https://api.nexusmods.com/v1/games/{game_id}/mods/{mod_id}/files/{file_id}/download_link.json"
    json = nexus_request(url)
    path = (dest / file) if file else (dest / filename(game_id, mod_id, file_id))
    with open(path, "wb") as f:
        data = json.json()
        download_url = ""
        for item in data:
            if item.get("short_name") == "Nexus CDN":
                download_url = item.get("URI", "")
                break
        if not download_url:
            logger.error("Nexus CDN download URL not found in Nexus response.")
            raise Exception("Nexus CDN download URL not found.")
        download_url = download_url.replace("\\u0026", "&")
        logger.info(f"Downloading from {download_url} to {path}")
        response = requests.get(download_url, headers=header(), stream=True)
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
