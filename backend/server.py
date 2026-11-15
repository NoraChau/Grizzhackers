"""WebSocket server: the bridge between the mascot window and the agent.

Owner: Michael

Run from the repo root with the venv active:
    python -m backend.server

Docs (websockets 17.4, asyncio API):
https://websockets.readthedocs.io/en/stable/reference/asyncio/server.html

Flow for one request:
  mascot sends USER_TEXT
    -> start run_agent on a worker thread (asyncio.to_thread)
    -> the agent calls set_state(...)  -> we send STATE to the mascot
    -> the agent calls confirm(question) -> we send CONFIRM_REQUEST and wait for the
       CONFIRM_RESPONSE with the same id
    -> run_agent returns the reply     -> we send REPLY (and speak it once TTS works)

Threads: run_agent is blocking code, so it runs on a worker thread. Its callbacks
(set_state, confirm) are called on that worker thread, so they hand work back to the
event loop with asyncio.run_coroutine_threadsafe(...).

Security:
  - Bind to 127.0.0.1 only (protocol.WS_HOST). This server can drive the whole PC.
  - Any web page in the user's browser can ALSO connect to ws://127.0.0.1. We log the
    Origin header of every connection; once you've seen what the mascot sends, put it in
    ALLOWED_ORIGINS so only the mascot window gets in.
"""

import asyncio
import logging
import uuid
from typing import Any

from dotenv import load_dotenv
from websockets.asyncio.server import ServerConnection, serve
from websockets.exceptions import ConnectionClosed

load_dotenv()  # before importing the agent: it reads LLM_* env vars at import time

from backend import protocol
from backend.agent.loop import run_agent
from backend.voice.hotkey import start_push_to_talk
from backend.voice.stt import transcribe

logger = logging.getLogger(__name__)

# How long to wait for the user to press Yes/No before treating it as "no".
CONFIRM_TIMEOUT_S = 60

# None = allow any Origin (just log it). Set to e.g. ["file://"] once you know what the
# mascot window sends. websockets rejects connections whose Origin isn't in the list.
ALLOWED_ORIGINS: list[str | None] | None = None


async def send(websocket: ServerConnection, type_: str, payload: dict[str, Any]) -> None:
    """Encode one message and send it to the mascot. Silently drop it if the mascot left."""
    try:
        await websocket.send(protocol.encode(type_, payload))
    except ConnectionClosed:
        logger.info("dropped %s: mascot disconnected", type_)


class Session:
    """State for one mascot connection: the running request and any open yes/no questions."""

    def __init__(self, websocket: ServerConnection) -> None:
        self.websocket = websocket
        self.loop = asyncio.get_running_loop()
        self.agent_task: asyncio.Task[None] | None = None
        # confirm id -> Future that resolves to True (yes) / False (no)
        self.pending_confirms: dict[str, asyncio.Future[bool]] = {}

    # ---- callbacks the agent calls from its worker thread ----

    def set_state(self, state: str) -> None:
        """Agent -> mascot: change the bear's look. Called on the worker thread."""
        future = asyncio.run_coroutine_threadsafe(
            send(self.websocket, protocol.STATE, {"state": state}), self.loop
        )
        future.result()  # wait so states arrive in order

    def confirm(self, question: str) -> bool:
        """Agent -> mascot: ask yes/no and block the worker thread until the user answers."""
        future = asyncio.run_coroutine_threadsafe(self.ask_mascot(question), self.loop)
        return future.result()

    # ---- runs on the event loop ----

    async def ask_mascot(self, question: str) -> bool:
        """Send CONFIRM_REQUEST and wait for the matching CONFIRM_RESPONSE."""
        confirm_id = uuid.uuid4().hex
        answer: asyncio.Future[bool] = self.loop.create_future()
        self.pending_confirms[confirm_id] = answer

        await send(self.websocket, protocol.STATE, {"state": "confirm"})
        await send(self.websocket, protocol.CONFIRM_REQUEST, {"id": confirm_id, "question": question})

        try:
            approved = await asyncio.wait_for(answer, timeout=CONFIRM_TIMEOUT_S)
        except TimeoutError:
            logger.info("confirm %s timed out, treating as no", confirm_id)
            approved = False
        finally:
            self.pending_confirms.pop(confirm_id, None)

        logger.info("confirm %r -> %s", question, approved)
        await send(self.websocket, protocol.STATE, {"state": "thinking"})
        return approved

    def answer_confirm(self, payload: dict[str, Any]) -> None:
        """Handle CONFIRM_RESPONSE from the mascot: wake up whoever is waiting on that id."""
        answer = self.pending_confirms.get(str(payload.get("id")))
        if answer is not None and not answer.done():
            answer.set_result(payload.get("approved") is True)

    async def handle_user_text(self, text: str) -> None:
        """Run one request through the agent and send the reply."""
        logger.info("user_text: %s", text)
        try:
            reply = await asyncio.to_thread(run_agent, text, self.confirm, self.set_state)
        except Exception:  # noqa: BLE001 - never let one bad request kill the connection
            logger.exception("agent crashed")
            reply = "Sorry, something went wrong on my end."
            await send(self.websocket, protocol.STATE, {"state": "idle"})

        logger.info("reply: %s", reply)
        await send(self.websocket, protocol.REPLY, {"text": reply})
        # TODO(Michael): once voice/tts.py works:
        #   await send(..., STATE "talking"); await asyncio.to_thread(speak, reply);
        #   await send(..., STATE "idle")

    def start_request(self, text: str) -> bool:
        """Start the agent in the background. Returns False if it's already busy."""
        if self.agent_task is not None and not self.agent_task.done():
            return False
        self.agent_task = asyncio.create_task(self.handle_user_text(text))
        return True

    def is_busy(self) -> bool:
        return self.agent_task is not None and not self.agent_task.done()

    def close(self) -> None:
        """Mascot disconnected: answer "no" to open questions so the agent thread can finish."""
        for answer in self.pending_confirms.values():
            if not answer.done():
                answer.set_result(False)


# Push-to-talk is one global key, not tied to a connection, so voice requests go to the
# most recently connected mascot window.
current_session: Session | None = None


async def handle_voice(wav_bytes: bytes) -> None:
    """Push-to-talk clip -> text -> same path as a typed USER_TEXT."""
    session = current_session
    if session is None:
        logger.info("heard push-to-talk but no mascot is connected")
        return
    ws = session.websocket
    if session.is_busy():
        await send(ws, protocol.REPLY, {"text": "I'm still working on the last thing. One moment!"})
        return

    await send(ws, protocol.STATE, {"state": "thinking"})
    text = await asyncio.to_thread(transcribe, wav_bytes)  # network call: keep it off the loop
    if not text:
        await send(ws, protocol.REPLY, {"text": "Sorry, I didn't catch that. Try again?"})
        await send(ws, protocol.STATE, {"state": "idle"})
        return

    await send(ws, protocol.TRANSCRIPT, {"text": text})
    if not session.start_request(text):
        await send(ws, protocol.REPLY, {"text": "I'm still working on the last thing. One moment!"})


async def handler(websocket: ServerConnection) -> None:
    """Handle one mascot connection: read messages and dispatch them by type.

    The agent runs as a background task, so this loop keeps reading while it works.
    That's what lets a CONFIRM_RESPONSE arrive in the middle of a request.
    """
    global current_session
    logger.info("mascot connected, origin=%r", websocket.request.headers.get("Origin"))
    session = Session(websocket)
    current_session = session

    try:
        async for raw in websocket:
            try:
                msg = protocol.decode(str(raw))
            except ValueError as exc:
                await send(websocket, protocol.ERROR, {"message": str(exc)})
                continue

            payload = msg["payload"]

            if msg["type"] == protocol.USER_TEXT:
                text = str(payload.get("text", "")).strip()
                if not text:
                    continue
                if not session.start_request(text):
                    await send(websocket, protocol.REPLY,
                               {"text": "I'm still working on the last thing. One moment!"})

            elif msg["type"] == protocol.CONFIRM_RESPONSE:
                session.answer_confirm(payload)

            else:
                await send(websocket, protocol.ERROR, {"message": f"unknown type: {msg['type']}"})
    finally:
        session.close()
        if current_session is session:
            current_session = None
        logger.info("mascot disconnected")


async def main() -> None:
    """Set up logging, start push-to-talk, and serve WebSockets forever."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s: %(message)s")

    # The push-to-talk callback runs on the keyboard thread: hand the clip to the event loop.
    loop = asyncio.get_running_loop()
    try:
        start_push_to_talk(lambda wav: asyncio.run_coroutine_threadsafe(handle_voice(wav), loop))
    except Exception:  # noqa: BLE001 - typing still works without voice
        logger.exception("push-to-talk failed to start; typing still works")

    async with serve(handler, protocol.WS_HOST, protocol.WS_PORT, origins=ALLOWED_ORIGINS) as server:
        logger.info("listening on ws://%s:%s", protocol.WS_HOST, protocol.WS_PORT)
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
