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
        The response from the GET request.
    """

    headers = header()
    logger.debug(f"Performing Nexus GET request to: {url}")
    response = requests.get(url, headers=headers)
    logger.debug(
        f"Nexus request returned status: {response.status_code} for URL: {url}"
    )
    return response


def get_filename(response: requests.Response) -> str:
    """
    Retrieves the filename for a specific mod file from Nexus Mods.

    Parameters
    ----------
    response : requests.Response
        The response containing file information.

    Returns
    -------
    str
        The filename of the specified mod file.
    """

    return str(from_json(response).get("file_name", ""))


def nexus_download(
    game_slug: str, mod_id: str, file_id: str, dest: Path, filename: Optional[str]
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
    """

    url = f"https://api.nexusmods.com/v1/games/{game_slug}/mods/{mod_id}/files/{file_id}/download_link.json"
    logger.info(
        f"Requesting Nexus download metadata for {game_slug} mod {mod_id} file {file_id}"
    )
    response = nexus_request(url)
    filename = filename if filename else get_filename(response)
    path = dest / filename
    logger.debug(f"Resolved filename '{filename}', target path: {path}")
    download_url = None
    for item in from_json(response):
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
