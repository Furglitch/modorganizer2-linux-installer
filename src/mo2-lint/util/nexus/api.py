#!/usr/bin/env python3

from loguru import logger
from util import state_file as state
from uuid import UUID, uuid4 as new_uuid
import json
import websockets.sync.client as websockets


def id() -> UUID:
    """
    Checks for an existing Nexus UUID in the state.\n
    If none exists, generates a new UUID and stores it in the state.

    Returns
    -------
    UUID
        The Nexus API UUID.
    """

    id = state.state_file.nexus_api.uuid if state.state_file.nexus_api else None
    if not id:
        logger.trace("No existing Nexus UUID found. Generating a new one.")
        id = new_uuid()
    state.state_file.nexus_api.uuid = id
    return id


def connection_token() -> str:
    """
    Checks for an existing connection token in the state.\n
    If none exists, requests a new connection token via WebSocket and stores it in the state.

    Returns
    -------
    str
        The Nexus connection token.
    """

    token = state.state_file.nexus_api.connection_token
    if not token:
        logger.trace("No existing Nexus connection token found. Requesting a new one.")
        token = request_connection_token()
    state.state_file.nexus_api.connection_token = token
    return token


def request_connection_token() -> str:
    """
    Requests a new connection token from the Nexus SSO WebSocket server.

    Returns
    -------
    str
        The requested Nexus connection token.
    """

    uuid = state.state_file.nexus_api.uuid if state.state_file.nexus_api.uuid else id()
    with websockets.connect("wss://sso.nexusmods.com") as socket:
        socket.send(
            {
                "id": str(uuid),
                "protocol": 2,
            }
        )
        for message in socket:
            response = message
            token = response.get("data", {}).get("connection_token")
            if token:
                socket.close()
                break
    return token


def api_key() -> str:
    """
    Checks for an existing API key in the state.\n
    If none exists, requests a new API key via WebSocket and stores it in the state.

    Returns
    -------
    str
        The Nexus API key.
    """

    key = state.state_file.nexus_api.api_key
    if not key:
        logger.trace("No existing Nexus API key found. Requesting a new one.")
        key = request_api_key()
    state.state_file.nexus_api.api_key = key
    return key


def request_api_key() -> str:
    """
    Requests a new API key from the Nexus SSO WebSocket server.

    Returns
    -------
    str
        The requested Nexus API key.
    """

    uuid = state.state_file.nexus_api.uuid if state.state_file.nexus_api.uuid else id()
    token = (
        state.state_file.nexus_api.connection_token
        if state.state_file.nexus_api.connection_token
        else request_connection_token()
    )
    with websockets.connect("wss://sso.nexusmods.com") as socket:
        socket.send(
            {
                "id": str(uuid),
                "token": token,
                "protocol": 2,
            }
        )
        for message in socket:
            response = json.loads(message)
            key = response.get("data", {}).get("api_key") or None
            if key:
                socket.close()
                break
    return key
