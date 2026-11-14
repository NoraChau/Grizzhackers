"""Safety: destructive tool calls need a "yes" from the user before they run. Never skip this.

Round trip:
    agent --confirm_request--> overlay shows Yes / No --confirm_response--> agent

Owner: Jay (the waiting part touches server.py, so pair with Michael)
"""

from typing import Any

from backend.protocol import SendFn

# Tool names that always need confirmation. Add to this whenever you write a risky tool.
DESTRUCTIVE_TOOLS: set[str] = {"close_app", "delete_note"}

CONFIRM_TIMEOUT_SECONDS = 30  # no answer in time counts as "no"


def needs_confirmation(tool_name: str, args: dict[str, Any]) -> bool:
    """Return True if this tool call must be confirmed by the user before it runs.

    TODO(exp1): start with the DESTRUCTIVE_TOOLS set. Later, also look at args
    (e.g. press_keys with ctrl+w could close unsaved work).
    """
    raise NotImplementedError("TODO(exp1): needs_confirmation")


def describe_for_user(tool_name: str, args: dict[str, Any]) -> str:
    """Turn a tool call into a short yes/no question, e.g. "Delete the note 'groceries'?".

    TODO(exp1)
    """
    raise NotImplementedError("TODO(exp1): describe_for_user")


async def ask_user(send: SendFn, tool_name: str, args: dict[str, Any]) -> bool:
    """Send a confirm_request and wait for the matching confirm_response. True means approved.

    TODO(exp1 + exp2):
    - Make a unique id; send "confirm_request" with id, tool, and describe_for_user().
    - Wait until server.py receives a "confirm_response" with the same id
      (hint: an asyncio.Future stored in a dict keyed by id).
    - Timeout or disconnect -> return False. Never assume yes.
    """
    raise NotImplementedError("TODO(exp1): ask_user")
