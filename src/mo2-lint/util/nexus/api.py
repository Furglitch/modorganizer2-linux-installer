#!/usr/bin/env python3

from loguru import logger
import uuid
import json
import websockets.sync.client as websockets
import webbrowser
from ..state import state_file as state

api_info = {}


def load_state() -> dict:
    global api_info
    state.load_state()
    api_info = state.nexus_api


def nexus_uuid() -> uuid.UUID:
    id_str = api_info.get("uuid", "")
    if id_str:
        id = uuid.UUID(id_str)
        logger.trace(f"Loaded existing Nexus UUID: {id}")
    else:
        id = uuid.uuid4()
        logger.trace(f"Created new Nexus UUID: {id}")

    if id:
        api_info["uuid"] = str(id)
        state.set_nexus_uuid(id)
        return id
    else:
        raise Exception("Failed to generate or load Nexus UUID.")


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
    if token:
        api_info["connection_token"] = token
        state.set_nexus_connection_token(token)
        return token
    else:
        raise Exception("Failed to generate or load connection token.")


def request_connection_token() -> str:
    id = api_info.get("uuid", "") if api_info.get("uuid") else nexus_uuid()
    with websockets.connect("wss://sso.nexusmods.com") as socket:
        socket.send(
            json.dumps(
                {
                    "id": id,
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
    token = api_info.get("api_key", "")
    if not token:
        try:
            token = request_nexus_key()
            logger.trace(f"Requested api token: {token}")
        except Exception as e:
            logger.error(f"Error requesting api token: {e}")
    else:
        logger.trace(f"Loaded existing api token: {token}")
    if token:
        api_info["api_key"] = token
        state.set_nexus_api_key(token)
        return token
    else:
        raise Exception("Failed to grab api token.")


def request_nexus_key() -> str:
    key = None
    id = api_info.get("uuid") if api_info.get("uuid") else nexus_uuid()
    token = (
        api_info.get("connection_token")
        if api_info.get("connection_token")
        else connection_token()
    )
    url = f"https://www.nexusmods.com/sso?id={str(id)}&application=mo2lint"
    webbrowser.open_new_tab(url)
    try:
        with websockets.connect("wss://sso.nexusmods.com") as socket:
            socket.send(
                json.dumps(
                    {
                        "id": str(id),
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
    api_info["api_key"] = key
    print("Key obtained:", key)
    return key


def main():
    load_state()
    api_key = api_info.get("api_key") if api_info.get("api_key") else nexus_key()
    print(api_info)
    return api_key
