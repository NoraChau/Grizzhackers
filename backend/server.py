"""WebSocket server: the bridge between the mascot window and the agent.

Owner: Michael

Run from the repo root with the venv active:
    python -m backend.server

Docs (websockets 17.4, asyncio API):
https://websockets.readthedocs.io/en/stable/reference/asyncio/server.html
    from websockets.asyncio.server import serve
    async with serve(handler, protocol.WS_HOST, protocol.WS_PORT) as server:
        await server.serve_forever()

What it does:
  - mascot sends USER_TEXT -> send STATE "thinking" -> run the agent -> send REPLY
    -> speak it (STATE "talking") -> STATE "idle"
  - push-to-talk (voice/hotkey.py) -> STT -> send TRANSCRIPT -> same path as USER_TEXT
  - the agent wants to do something destructive -> send CONFIRM_REQUEST (STATE "confirm")
    and wait for the CONFIRM_RESPONSE with the same id

Threads gotcha: agent.loop.run_agent is normal blocking code. Run it with
`await asyncio.to_thread(run_agent, ...)` so the server can still receive the user's yes/no
while the agent waits. The confirm callback then runs on that worker thread: use
asyncio.run_coroutine_threadsafe(ask_mascot(question), loop).result() to wait for the answer.

Security:
  - Bind to 127.0.0.1 only (protocol.WS_HOST). This server can drive the whole PC.
  - Any web page open in the user's browser can ALSO connect to ws://127.0.0.1. Check the
    Origin header (serve(..., origins=[...])) so only the mascot window gets in: log the
    Origin the mascot sends, then allow only that.
"""

import asyncio
import logging
from typing import Any

from dotenv import load_dotenv
from websockets.asyncio.server import ServerConnection, serve

from backend import protocol

logger = logging.getLogger(__name__)


async def send(websocket: ServerConnection, type_: str, payload: dict[str, Any]) -> None:
    """Encode one message and send it to the mascot."""
    await websocket.send(protocol.encode(type_, payload))


async def handler(websocket: ServerConnection) -> None:
    """Handle one mascot connection: read messages, dispatch by type, send replies.

    ECHO VERSION: replies "You said: ..." until the agent is wired in.
    TODO(Michael): replace the echo with run_agent via asyncio.to_thread, and handle
    CONFIRM_RESPONSE.
    """
    logger.info("mascot connected")

    async for raw in websocket:
        try:
            msg = protocol.decode(str(raw))
        except ValueError as exc:
            await send(websocket, protocol.ERROR, {"message": str(exc)})
            continue

        if msg["type"] == protocol.USER_TEXT:
            text = msg["payload"].get("text", "")
            logger.info("user_text: %s", text)
            await send(websocket, protocol.STATE, {"state": "thinking"})
            await send(websocket, protocol.REPLY, {"text": f"You said: {text}"})
            await send(websocket, protocol.STATE, {"state": "idle"})
        else:
            await send(websocket, protocol.ERROR, {"message": f"unknown type: {msg['type']}"})

    logger.info("mascot disconnected")


async def main() -> None:
    """Load .env, set up logging, and serve WebSockets forever.

    TODO(Michael): start push-to-talk here once voice/hotkey.py works.
    """
    load_dotenv()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s: %(message)s")

    async with serve(handler, protocol.WS_HOST, protocol.WS_PORT) as server:
        logger.info("listening on ws://%s:%s", protocol.WS_HOST, protocol.WS_PORT)
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
