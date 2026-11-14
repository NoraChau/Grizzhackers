"""The agent loop: send the request to OpenAI, run the tools it asks for, repeat until done.

Owner: Jay
Docs: https://platform.openai.com/docs/guides/function-calling
Models: https://platform.openai.com/docs/models (pick one that supports tool calling)

4 PM milestone: typed "open Notepad and type hello" works end to end.
"""

from backend.protocol import SendFn

MODEL = ""  # TODO(exp1): choose a model
MAX_STEPS = 10  # safety net: stop after this many tool rounds so a confused model can't loop forever


async def run_agent(user_text: str, send: SendFn) -> str:
    """Handle one user request end to end and return the final reply (to be spoken).

    TODO(exp1): the tool-calling loop.
    - Use SYSTEM_PROMPT (agent/prompts.py) and TOOL_SCHEMAS / TOOL_FUNCTIONS (tools/__init__.py).
    - Before running a tool, check safety.needs_confirmation(); if True, ask the user first.
    - After each tool call: send a "step" message and log one line: tool, args, result, ms.
    - Tools block (pywinauto waits for windows), so run them with asyncio.to_thread()
      to keep the WebSocket responsive.
    - Send "status" messages ("thinking", "acting") so the orb shows what is happening.
    """
    raise NotImplementedError("TODO(exp1): agent loop")
