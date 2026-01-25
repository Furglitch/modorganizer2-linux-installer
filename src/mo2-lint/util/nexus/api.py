#!/usr/bin/env python3

import json
from util.state_file import state_file as state
from uuid import UUID, uuid4 as new_uuid
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

    id = state.nexus_api.uuid
    if not id:
        id = new_uuid()
    state.nexus_api.uuid = id
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

    token = state.nexus_api.connection_token
    if not token:
        token = request_connection_token()
    state.nexus_api.connection_token = token
    return token


def request_connection_token() -> str:
    """
    Requests a new connection token from the Nexus SSO WebSocket server.

    Returns
    -------
    str
        The requested Nexus connection token.
    """

    uuid = state.nexus_api.uuid if state.nexus_api.uuid else id()
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

    key = state.nexus_api.api_key
    if not key:
        key = request_api_key()
    state.nexus_api.api_key = key
    return key


def request_api_key() -> str:
    """
    Requests a new API key from the Nexus SSO WebSocket server.

    Returns
    -------
    str
        The requested Nexus API key.
    """

    uuid = state.nexus_api.uuid if state.nexus_api.uuid else id()
    token = (
        state.nexus_api.connection_token
        if state.nexus_api.connection_token
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
