#!/usr/bin/env python3

from loguru import logger
from pydantic_core import from_json
from util import state_file as state
from uuid import UUID, uuid4 as new_uuid
import json
import webbrowser
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

    if state.state_file.nexus_api:
        if state.state_file.nexus_api.uuid:
            uuid = state.state_file.nexus_api.uuid
            logger.trace(f"Found existing Nexus API UUID in state file: {uuid}")
            return uuid
    else:
        state.state_file.nexus_api = state.NexusAPIData()
        logger.warning(
            "Ignore previous log message about missing Nexus API state - initialized new NexusAPIData in state file."
        )
        logger.trace("Initialized new NexusAPIData in state file.")

    uuid = new_uuid()
    state.state_file.nexus_api.uuid = uuid
    return uuid


def connection_token() -> str:
    """
    Checks for an existing connection token in the state.\n
    If none exists, initiates a request for a new one.

    Returns
    -------
    str
        The Nexus connection token.
    """

    if state.state_file.nexus_api:
        if state.state_file.nexus_api.connection_token:
            connection_token = state.state_file.nexus_api.connection_token
            logger.trace("Found existing Nexus connection token in state file.")
            return connection_token

    connection_token = request_connection_token()
    state.state_file.nexus_api.connection_token = connection_token
    return connection_token


def request_connection_token() -> str:
    """
    Connects to the Nexus SSO WebSocket server to request a new connection token.

    Returns
    -------
    str
        The requested Nexus connection token.
    """

    uuid = id()
    logger.info(f"Requesting new Nexus connection token with UUID: {uuid}")
    with websockets.connect("wss://sso.nexusmods.com") as socket:
        logger.trace("Connected to Nexus SSO WebSocket server.")
        socket.send(
            json.dumps(
                {
                    "id": str(uuid),
                    "protocol": 2,
                }
            )
        )
        logger.trace("Sent connection token request to Nexus SSO WebSocket server.")
        message = socket.recv()
        socket.close()
    response = from_json(message)
    logger.trace("Received response from Nexus SSO WebSocket server")
    token = response.get("data", {}).get("connection_token") or None
    if token:
        logger.success("Successfully obtained Nexus connection token.")
    return token


def api_key() -> str:
    """
    Checks for an existing API key in the state.\n
    If none exists, initiates a request for a new one.

    Returns
    -------
    str
        The Nexus API key.
    """

    if state.state_file.nexus_api:
        if state.state_file.nexus_api.api_key:
            api_key = state.state_file.nexus_api.api_key
            logger.trace("Found existing Nexus API key in state file.")
            return api_key

    api_key = request_api_key()
    state.state_file.nexus_api.api_key = api_key
    state.write_state(False)
    return api_key


def request_api_key() -> str:
    """
    Connects to the Nexus SSO WebSocket server to request a new API key.

    Returns
    -------
    str
        The requested Nexus API key.
    """

    uuid = str(id())
    token = connection_token()
    key = ""
    logger.info(f"Requesting new Nexus API key with UUID: {uuid} and connection token")
    with websockets.connect("wss://sso.nexusmods.com") as socket:
        logger.trace("Connected to Nexus SSO WebSocket server.")
        socket.send(
            json.dumps(
                {
                    "id": uuid,
                    "token": token,
                    "protocol": 2,
                }
            )
        )
        logger.trace("Sent API key request to Nexus SSO WebSocket server.")

        try:
            logger.info("Opening web browser for Nexus SSO authentication.")
            webbrowser.open(
                "https://www.nexusmods.com/sso?id=" + uuid + "&application=mo2lint"
            )
            message = socket.recv()
        except Exception as e:
            logger.exception(
                f"Error while waiting for response from Nexus SSO WebSocket server: {e}"
            )
            return ""
        finally:
            logger.trace("Closing Nexus SSO WebSocket connection.")
            socket.close()

    response = from_json(message)
    key = response.get("data", {}).get("api_key") or None
    logger.trace("Received response from Nexus SSO WebSocket server")
    if key:
        logger.success("Successfully obtained Nexus API key.")
    return key
