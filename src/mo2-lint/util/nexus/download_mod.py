#!/usr/bin/env python3

from click import Path
from loguru import logger
from pydantic_core import from_json
from typing import Optional
from util import variables as var
from util.nexus.api import api_key
import requests


def header() -> dict:
    """
    Constructs the headers required for Nexus Mods API requests.

    Returns
    -------
    dict
        The constructed header.
    """

    key = api_key()
    logger.debug(f"Building Nexus Mods API headers (Application-Version={var.version})")
    header = {
        "apikey": f"{key}",
        "Application-Name": "mo2lint",
        "Application-Version": var.version,
    }
    return header


def nexus_request(url: str) -> requests.Response:
    """
    Makes a GET request to the specified Nexus Mods API URL with the appropriate headers.

    Parameters
    ----------
    url : str
        The URL to send the GET request to.

    Returns
    -------
    Response
        The response from the GET request. Use pydantic_core.from_json() to parse the JSON content.
    """

    headers = header()
    logger.debug(f"Performing Nexus request to: {url}")
    response = requests.get(url, headers=headers)
    logger.debug(
        f"Nexus request returned status: {response.status_code} for URL: {url}"
    )
    return response


def get_filename(game_slug: str, mod_id: str, file_id: str) -> str:
    """
    Retrieves the filename for a specific mod file from Nexus Mods.

    Parameters
    ----------
    game_slug : str
        The Nexus Mods game slug.
    mod_id : str
        The ID of the mod.
    file_id : str
        The ID of the file.

    Returns
    -------
    str
        The filename of the specified mod file.
    """

    url = f"https://api.nexusmods.com/v1/games/{game_slug}/mods/{mod_id}/files/{file_id}.json"
    response = nexus_request(url)
    filename = from_json(response.content).get("file_name", "")
    return filename


def nexus_download(
    game_slug: str,
    mod_id: str,
    file_id: str,
    dest: Path,
    filename: Optional[str] = None,
) -> str:
    """
    Downloads a mod file from Nexus Mods to the specified destination.

    Parameters
    ----------
    game_slug : str
        The Nexus Mods game slug.
    mod_id : str
        The ID of the mod.
    file_id : str
        The ID of the file.
    dest : Path
        The destination path to save the downloaded file.
    filename : str, optional
        The name to save the file as. If not provided, the original filename will be used.

    Returns
    -------
    str
        The filename of the downloaded file.
    """

    url = f"https://api.nexusmods.com/v1/games/{game_slug}/mods/{mod_id}/files/{file_id}/download_link.json"
    logger.info(
        f"Requesting Nexus download metadata for {game_slug} mod {mod_id} file {file_id}"
    )
    response = nexus_request(url)
    if not filename:
        filename = get_filename(game_slug, mod_id, file_id)
    path = dest / filename
    logger.debug(f"Resolved filename '{filename}', target path: {path}")
    download_url = None
    for item in from_json(response.content):
        if item.get("short_name") == "Nexus CDN":
            download_url = item.get("URI", "").replace("\\u0026", "&")
            break
    if not download_url:
        logger.error("No valid Nexus CDN download URL found in response.")
        raise ValueError("No valid download URL found for the specified file.")
    logger.debug(f"Beginning download from {download_url} to {path}")
    with open(path, "wb") as f:
        download = requests.get(download_url, headers=header(), stream=True)
        for chunk in download.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    logger.info(f"Completed download to {path}")
    return filename
