#!/usr/bin/env python3

from loguru import logger
from pathlib import Path
import uuid
import json
import websockets.sync.client as websockets
from ..state import state_file as state

state_file: Path = None
api_info = {}


def load_state() -> dict:
    global api_info
    global state_file
    state_file = state.state_file
    with state_file.open("r", encoding="utf-8") as f:
        api_info = json.load(f).get("nexus_api", {})


def nexus_uuid() -> uuid.UUID:
    id_str = api_info.get("uuid", "")
    if id_str:
        id = uuid.UUID(id_str)
        logger.trace(f"Loaded existing Nexus UUID: {id}")
    else:
        id = uuid.uuid4()
        logger.trace(f"Created new Nexus UUID: {id}")
    state.set_nexus_uuid(id)
    api_info["uuid"] = str(id)
    return id


def connection_token() -> str:
    token = api_info.get("connection_token", "")
    if not token:
        try:
            token = request_connection_token()
            logger.trace(f"Requested connection token: {token}")
        except Exception as e:
            logger.error(f"Error requesting connection token: {e}")
    else:
        logger.trace(f"Loaded existing connection token: {token}")
    state.set_nexus_connection_token(token)
    api_info["connection_token"] = token
    return token


def request_connection_token() -> str:
    with websockets.connect("wss://sso.nexusmods.com") as socket:
        socket.send(
            json.dumps(
                {
                    "id": api_info.get("uuid", ""),
                    "protocol": 2,
                }
            )
        )
        for message in socket:
            logger.trace(f"Message: {message}")
            response = json.loads(message)
            token = response.get("data", {}).get("connection_token")
            if token:
                socket.close()
                break
    return token


def nexus_key() -> str:
    key = api_info.get("api_key", "")
    if not key:
        try:
            key = request_nexus_key()
            logger.trace(f"Requested Nexus API key: {key}")
        except Exception as e:
            key = None
            logger.error(f"Error requesting Nexus API key: {e}")
    else:
        logger.trace(f"Loaded existing Nexus API key: {key}")
    state.set_nexus_api_key(key)
    api_info["api_key"] = key
    return key


def request_nexus_key() -> str:
    import webbrowser

    key = None
    id = api_info.get("uuid")
    token = api_info.get("connection_token")
    url = f"https://www.nexusmods.com/sso?id={str(id)}&application=mo2lint"
    webbrowser.open(url)
    try:
        with websockets.connect("wss://sso.nexusmods.com") as socket:
            socket.send(
                json.dumps(
                    {
                        "id": id,
                        "token": token,
                        "protocol": 2,
                    }
                )
            )
            logger.info("Waiting for user to authorize in the browser...")
            for message in socket:
                response = json.loads(message)
                data = response.get("data", {})
                key = data.get("api_key")
                if key:
                    socket.close()
                    break
    except Exception as e:
        logger.error(f"WebSocket error during SSO: {e}")
    return key


def main():
    load_state()
    if nexus_uuid():
        if connection_token():
            if nexus_key():
                logger.info("Nexus API credentials successfully obtained and stored.")
            else:
                logger.error("Failed to obtain Nexus API key.")
        else:
            logger.error("Failed to obtain connection token.")
    else:
        logger.error("Failed to create Nexus UUID.")
