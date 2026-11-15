"""The agent loop: send the request to gpt-oss, run the tools it asks for, repeat.

Owner: Jay. Write the loop yourself; no agent frameworks.

One request, step by step:
  1. messages = [{"role": "system", ...SYSTEM_PROMPT}, {"role": "user", ...user_text}]
  2. response = client.chat.completions.create(model=..., messages=messages,
                                               tools=TOOLS, tool_choice="auto")
  3. msg = response.choices[0].message
       - no msg.tool_calls -> msg.content is the final reply. Done.
       - otherwise append msg (with its tool_calls) to messages, then for EACH call:
         run it and append {"role": "tool", "tool_call_id": call.id, "content": result}
  4. Go back to 2, at most MAX_STEPS times.

Docs:
  - Tool calling with Chat Completions: https://platform.openai.com/docs/guides/function-calling
  - openai Python SDK: https://github.com/openai/openai-python
  - gpt-oss on vLLM (tool-calling flags): https://docs.vllm.ai/projects/recipes/en/latest/OpenAI/GPT-OSS.html

Terminal mode, no mascot needed (the 7:30 PM milestone). From the repo root:
    python -m backend.agent.loop
"""

import logging
import os

from collections.abc import Callable
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

logger = logging.getLogger(__name__)

MAX_STEPS = 8

# Ask the user a yes/no question and return True for yes. server.py routes it to the
# mascot's yes/no buttons; terminal mode just uses input().
ConfirmFn = Callable[[str], bool]

# Tell the mascot what we're doing: "thinking", "idle", ... (see protocol.MascotState).
StateFn = Callable[[str], None]

load_dotenv()

MODEL = os.environ["LLM_MODEL"]

def make_client() -> OpenAI:
    return OpenAI(base_url=os.environ["LLM_BASE_URL"], api_key=os.environ["LLM_API_KEY"])

def needs_confirmation(tool_name: str, args: dict[str, Any]) -> str | None:
    DANGER_WORDS = {}
    DANGER_KEYS = {}

    if (tool_name == "press_keys"):
        keys = args.get("keys", "").lower()
        if (keys in DANGER_KEYS):
            return f"Press {keys}? This is a destructive action that could close or delete something."

    if (tool_name == "click_control"):
        label = args.get("name" , "").lower()
        if (label in DANGER_WORDS):
            return f"Click {label}? This is a destructive action that could send or delete something."

    return None


def run_tool(name: str, arguments: str) -> str:
    start =


def run_agent(user_text: str, confirm: ConfirmFn, set_state: StateFn) -> str:
    """Handle one user request end to end and return the reply text for the bubble.

    This is normal (blocking) code. server.py runs it in a worker thread.

    TODO(Jay): the loop described at the top of this file. Use prompt.SYSTEM_PROMPT and
    tool_schemas.TOOLS, the model name from os.environ["LLM_MODEL"], and stop after
    MAX_STEPS with a friendly "I couldn't finish that" reply.
    """
    raise NotImplementedError("TODO(Jay): run_agent")


def main() -> None:
    """Terminal mode: type a request, see the reply. No mascot or voice needed.

    TODO(Jay): load .env (python-dotenv's load_dotenv), turn on logging
    (logging.basicConfig(level=logging.INFO)), then loop: input() -> run_agent -> print.
    For confirm, ask in the terminal: input(question + " [y/n] ").
    """
    raise NotImplementedError("TODO(Jay): terminal mode")


if __name__ == "__main__":
    main()
