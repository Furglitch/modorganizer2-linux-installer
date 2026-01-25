#!/usr/bin/env python3

from typing import Optional

from click import Path
from .api import api_key
from util.variables import version
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
    header = {
        "apikey": f"{key}",
        "Application-Name": "mo2lint",
        "Application-Version": version,
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
    response = requests.get(url, headers=headers)
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

    return str(response.json().get("file_name", ""))


def nexus_download(
    game_slug: str, mod_id: str, file_id: str, dest: Path, filename: Optional[str]
):
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
    response = nexus_request(url)
    filename = filename if filename else get_filename(response)
    path = dest / filename
    for item in response.json():
        download_url = (
            item.get("URI", "").replace("\\u0026", "&")
            if item.get("short_name") == "Nexus CDN"
            else None
        )
    if not download_url:
        raise Exception("Nexus CDN download URL not found.")
    with open(path, "wb") as f:
        download = requests.get(download_url, headers=header(), stream=True)
        for chunk in download.iter_content(chunk_size=8192):
            f.write(chunk)
