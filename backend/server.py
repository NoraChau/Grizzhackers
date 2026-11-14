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

logger = logging.getLogger(__name__)


async def handler(websocket) -> None:
    """Handle one mascot connection: read messages, dispatch by type, send replies.

    TODO(Michael): for each raw message: protocol.decode -> act on USER_TEXT /
    CONFIRM_RESPONSE. Bad message -> send an ERROR message back, keep the connection open.
    """
    raise NotImplementedError("TODO(Michael): handler")


async def main() -> None:
    """Load .env, set up logging, start push-to-talk, and serve WebSockets forever.

    TODO(Michael): implement (see the docs snippet at the top of this file).
    """
    raise NotImplementedError("TODO(Michael): server main")


if __name__ == "__main__":
    asyncio.run(main())
