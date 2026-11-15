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

import json
import logging
import os
import time
from collections.abc import Callable
from typing import Any

from dotenv import load_dotenv
from openai import APIConnectionError, APIStatusError, APITimeoutError, OpenAI

load_dotenv()

from backend.agent.prompt import SYSTEM_PROMPT
from backend.agent.tool_schemas import TOOL_FUNCTIONS, TOOLS
from backend.tools.keyboard_mouse import normalize_keys

logger = logging.getLogger(__name__)

MAX_STEPS = 8

# Ask the user a yes/no question and return True for yes. server.py routes it to the
# mascot's yes/no buttons; terminal mode just uses input().
ConfirmFn = Callable[[str], bool]

# Tell the mascot what we're doing: "thinking", "idle", ... (see protocol.MascotState).
StateFn = Callable[[str], None]

MODEL = os.environ["LLM_MODEL"]

def make_client() -> OpenAI:
    return OpenAI(base_url=os.environ["LLM_BASE_URL"], api_key=os.environ["LLM_API_KEY"])

CLIENT = make_client()

def needs_confirmation(tool_name: str, args: dict[str, Any]) -> str | None:
    DANGER_WORDS = {"delete", "send", "remove", "buy", "purchase", "pay", "close", "don't save", "discard"}
    DANGER_KEYS = {"alt+f4", "ctrl+w", "shift+delete", "delete"}

    if (tool_name == "press_keys"):
        keys = normalize_keys(args.get("keys", ""))
        if (keys in DANGER_KEYS):
            return f"Press {keys}? This is a destructive action that could close or delete something."

    if (tool_name == "click_control"):
        label = args.get("name" , "").lower()
        if any(word in label for word in DANGER_WORDS):
            return f"Click {label}? This is a destructive action that could send or delete something."

    return None


def run_tool(name: str, arguments: str) -> str:
    start = time.perf_counter()

    if (name not in TOOL_FUNCTIONS):
        result = f"Error: Unknown tool {name}"
    else:
        try:
            args = json.loads(arguments)
            if (not isinstance(args, dict)):
                result = "Error: Arguments must be a JSON object"
            else:
                result = TOOL_FUNCTIONS[name](**args)
        except json.JSONDecodeError:
            result = f"Error: Bad JSON arguments for {name}"
        except TypeError as e:
            result = f"Error: Wrong arguments for {name} : {e}"
        except Exception as e:  # noqa: BLE001
            result = f"Error: {name} failed: {e}"

    ms = (time.perf_counter() - start) * 1000
    logger.info("tool=%s args=%s result=%s ms=%d", name, arguments, result, ms)

    return str(result)

def run_agent(user_text: str, confirm: ConfirmFn, set_state: StateFn) -> str:
    set_state("thinking")
    messages: list[Any] = [{"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text}]

    try:
        for step in range(MAX_STEPS):
            try:
                resp = CLIENT.chat.completions.create(
                    model=MODEL,
                    messages=messages,
                    tools=TOOLS,
                    tool_choice="auto")
            except APIConnectionError, APITimeoutError, APIStatusError:
                return "Sorry, I can't reach my brain right now."

            msg = resp.choices[0].message
            messages.append({"role": "assistant", "content": msg.content,
                             "tool_calls": msg.tool_calls,
                             "reasoning": getattr(msg, "reasoning", None)})

            if (not msg.tool_calls):
                return msg.content or "Done!"

            for call in msg.tool_calls:
                name = call.function.name
                try:
                        args = json.loads(call.function.arguments)
                except json.JSONDecodeError:
                    args = {}
                if not isinstance(args, dict):
                    args = {}

                question = needs_confirmation(tool_name=name, args=args)

                if (question and confirm(question) is False):
                    result = "Error: The user said no, so I did not do it."
                else:
                    result = run_tool(name, call.function.arguments)

                messages.append({"role": "tool", "tool_call_id": call.id, "content": result})

        return "I couldn't finish that. Can you try a smaller step?"
    finally:
        set_state("idle")

def main() -> None:
    logging.basicConfig(level=logging.INFO)

    def terminal_confirm(question: str) -> bool:
        ans = input(question + " [y/n] ")
        ans = ans.strip().lower()
        return bool(ans.startswith("y"))

    def terminal_state(state) -> None:
        print("["+ state + "]")

    while(True):
        text = input("you> ").strip()
        if (not text):
            continue
        if (text in ("exit", "quit")):
            break
        reply = run_agent(text, terminal_confirm, terminal_state)
        print("grizz> " + reply)

if __name__ == "__main__":
    main()
