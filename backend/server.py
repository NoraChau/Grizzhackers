"""WebSocket server: the bridge between the overlay (Electron window) and the agent.

Run from the repo root:
    python -m backend.server

One typed command:
    overlay --user_text--> server --> agent.loop.run_agent() --> tools
    overlay <--status / transcript / step-- server <-- agent

Owner: Experienced #2
Docs (websockets 14+ asyncio API):
    https://websockets.readthedocs.io/en/stable/reference/asyncio/server.html
"""

import asyncio
import logging

from backend.protocol import WS_HOST, WS_PORT

log = logging.getLogger(__name__)


async def handle_connection(websocket) -> None:  # websocket: websockets ServerConnection
    """Handle one overlay connection: read messages until it disconnects.

    TODO(exp2):
    - Loop over incoming messages and decode them with protocol.decode().
    - "user_text"        -> run the agent (backend.agent.loop.run_agent)
    - "confirm_response" -> hand the answer to the waiting confirm (backend.agent.safety)
    - "cancel"           -> stop the running agent task
    - Send replies with protocol.encode().
    """
    raise NotImplementedError("TODO(exp2): handle_connection")


async def main() -> None:
    """Load .env, start push-to-talk, and serve WebSocket connections forever.

    TODO(exp2):
    - Call load_dotenv() (python-dotenv) first so os.environ has the API keys.
    - Serve on WS_HOST:WS_PORT.
    - SECURITY: any web page open in a browser can connect to ws://127.0.0.1. Since this server
      controls the computer, limit who can connect: see the `origins` argument of serve(),
      or have the overlay send a secret token as its first message.
    - Start backend.voice.push_to_talk.start_listening().
    """
    raise NotImplementedError(f"TODO(exp2): start the server on {WS_HOST}:{WS_PORT}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    asyncio.run(main())
