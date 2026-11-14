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
from collections.abc import Callable
from typing import Any

from openai import OpenAI

logger = logging.getLogger(__name__)

MAX_STEPS = 8

# Ask the user a yes/no question and return True for yes. server.py routes it to the
# mascot's yes/no buttons; terminal mode just uses input().
ConfirmFn = Callable[[str], bool]

# Tell the mascot what we're doing: "thinking", "idle", ... (see protocol.MascotState).
StateFn = Callable[[str], None]


def make_client() -> OpenAI:
    """Build the OpenAI client from env vars only (LLM_BASE_URL, LLM_API_KEY).

    Never hardcode the URL or the model name: switching to the Grok fallback must be a
    .env change, not a code change.

    TODO(Jay): scripts/smoke_test.py builds the same client. Look there.
    """
    raise NotImplementedError("TODO(Jay): make_client")


def needs_confirmation(tool_name: str, args: dict[str, Any]) -> str | None:
    """Return a yes/no question if this tool call could destroy or send something, else None.

    Destructive = delete, send, purchase, or close unsaved work. Examples:
    press_keys("alt+f4"), click_control(name="Send"), click_control(name="Delete").
    run_agent must ask with confirm() and skip the tool if the answer is no.
    Never skip this check (CLAUDE.md rule).

    TODO(Jay)
    """
    raise NotImplementedError("TODO(Jay): needs_confirmation")


def run_tool(name: str, arguments: str) -> str:
    """Run one tool call from the model and return its result as a short string.

    `arguments` is the raw JSON string from call.function.arguments, and it can be
    invalid JSON (models make mistakes). Unknown tool, bad JSON, or an exception inside
    the tool: return "error: ...", never raise into the loop.

    Log one line per call: tool name, args, result, and how long it took in ms
    (time.perf_counter()).

    TODO(Jay): look the function up in tool_schemas.TOOL_FUNCTIONS.
    """
    raise NotImplementedError("TODO(Jay): run_tool")


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
