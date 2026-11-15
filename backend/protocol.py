"""Message types shared by the backend and the mascot window.

Every WebSocket message is one JSON object:
    {"type": "<one of the names below>", "payload": {...}}

This list must match mascot/protocol.js. Add a type here -> add it there too.
Owner: Michael
"""

import json
from typing import Any, Literal, TypedDict

# Where the backend listens. mascot/protocol.js (WS_URL) and the CSP in mascot/index.html
# must use the same address.
# Security: localhost only. Never 0.0.0.0, or anyone on the venue Wi-Fi could drive this PC.
WS_HOST = "127.0.0.1"
WS_PORT = 8765

# ---- Mascot -> backend ----
USER_TEXT = "user_text"  # payload: {"text": str}             the user typed a request
CONFIRM_RESPONSE = "confirm_response"  # payload: {"id": str, "approved": bool}

# ---- Backend -> mascot ----
STATE = "state"  # payload: {"state": MascotState}             changes the bear's look
REPLY = "reply"  # payload: {"text": str}                       show in the speech bubble
TRANSCRIPT = "transcript"  # payload: {"text": str}             what speech-to-text heard
CONFIRM_REQUEST = "confirm_request"  # payload: {"id": str, "question": str}
ERROR = "error"  # payload: {"message": str}

MascotState = Literal["idle", "thinking", "talking", "confirm"]


class Message(TypedDict):
    type: str
    payload: dict[str, Any]


def encode(type_: str, payload: dict[str, Any]) -> str:
    """Build the JSON string to send over the WebSocket.

    json.dumps a dict with "type" and "payload".
    Docs: https://docs.python.org/3/library/json.html
    """
    
    message = {"type": type_, "payload": payload}
    return json.dumps(message)


def decode(raw: str) -> Message:
    """Parse a JSON string from the mascot into a Message.

    json.loads, then check it has "type" (a str) and "payload" (a dict).
    Bad input should raise ValueError so server.py can reply with an ERROR message
    instead of crashing.
    """

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"not valid JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise ValueError("message must be a JSON object")
    if not isinstance(data.get("type"), str):
        raise ValueError('message needs a "type" string')
    if not isinstance(data.get("payload"), dict):
        raise ValueError('message needs a "payload" object')

    return {"type": data["type"], "payload": data["payload"]}
