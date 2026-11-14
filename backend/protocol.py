"""Messages shared by the backend and the overlay.

Every message on the WebSocket is one JSON object:
    {"type": "<one of the names below>", "payload": {...}}

Keep this file in sync with overlay/src/protocol.ts. Add a type here -> add it there too.
Owner: Michael
"""

from collections.abc import Awaitable, Callable
from typing import Any, Literal, TypedDict

# Where the backend listens. overlay/src/protocol.ts (WS_URL) and the CSP in
# overlay/index.html must use the same address.
WS_HOST = "127.0.0.1"
WS_PORT = 8765

# ---- Overlay -> backend ----
USER_TEXT = "user_text"  # the user typed a command
CONFIRM_RESPONSE = "confirm_response"  # yes/no answer to a confirm_request
CANCEL = "cancel"  # stop whatever the agent is doing

# ---- Backend -> overlay ----
STATUS = "status"  # what the companion is doing right now (drives the orb)
TRANSCRIPT = "transcript"  # a line of conversation to show
STEP = "step"  # one tool call, for the step log
CONFIRM_REQUEST = "confirm_request"  # ask the user before a destructive action
ERROR = "error"  # something went wrong; show it to the user

AgentState = Literal["idle", "listening", "thinking", "acting", "speaking", "recording"]


class UserTextPayload(TypedDict):
    text: str


class ConfirmResponsePayload(TypedDict):
    id: str  # same id as the confirm_request it answers
    approved: bool


class StatusPayload(TypedDict):
    state: AgentState


class TranscriptPayload(TypedDict):
    role: Literal["user", "assistant"]
    text: str


class StepPayload(TypedDict):
    tool: str
    args: dict[str, Any]
    result: str
    ms: int


class ConfirmRequestPayload(TypedDict):
    id: str  # unique per request, so the answer can be matched to it
    tool: str
    summary: str  # plain English, e.g. "Delete the note 'groceries'?"


class ErrorPayload(TypedDict):
    message: str


class Message(TypedDict):
    type: str
    payload: dict[str, Any]


# A function that sends one message to the overlay: await send(STATUS, {"state": "thinking"})
# server.py creates it; the agent, safety, and voice code receive it.
SendFn = Callable[[str, dict[str, Any]], Awaitable[None]]


def encode(type_: str, payload: dict[str, Any]) -> str:
    """Build the JSON string to send over the WebSocket.

    TODO(exp2): use json.dumps to produce {"type": type_, "payload": payload}.
    """
    raise NotImplementedError("TODO(exp2): protocol.encode")


def decode(raw: str) -> Message:
    """Parse a JSON string from the overlay into a Message.

    TODO(exp2): json.loads, then check it has "type" (str) and "payload" (dict).
    Bad input should raise ValueError, not crash the server.
    """
    raise NotImplementedError("TODO(exp2): protocol.decode")
