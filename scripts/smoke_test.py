"""Smoke test: can this laptop reach our gpt-oss server and get a tool call back?

Run from the repo root with the venv active:
    python scripts/smoke_test.py

PASS = the model answered "Open Notepad" with a call to the open_app tool.
It never prints the server URL or the key (CLAUDE.md secrets rule).
Owner: Nora
"""

import os
import sys
import time
from pathlib import Path

import openai
from dotenv import load_dotenv
from openai import OpenAI

REPO_ROOT = Path(__file__).resolve().parent.parent
REQUIRED_VARS = ["LLM_BASE_URL", "LLM_API_KEY", "LLM_MODEL"]

# The same shape as the real schemas in backend/agent/tool_schemas.py.
TEST_TOOL = {
    "type": "function",
    "function": {
        "name": "open_app",
        "description": "Open a Windows app such as Notepad or Calculator.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "App name, e.g. 'notepad'."},
            },
            "required": ["name"],
            "additionalProperties": False,
        },
    },
}


def main() -> int:
    load_dotenv(REPO_ROOT / ".env")
    missing = [name for name in REQUIRED_VARS if not os.environ.get(name)]
    if missing:
        print(f"FAIL: missing in .env: {', '.join(missing)}")
        print("Copy .env.example to .env in the repo root and fill it in (ask Nora privately).")
        return 1

    client = OpenAI(
        base_url=os.environ["LLM_BASE_URL"],
        api_key=os.environ["LLM_API_KEY"],
        timeout=60,
    )
    model = os.environ["LLM_MODEL"]
    print(f"Asking model {model!r} to open Notepad...")

    start = time.perf_counter()
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Open Notepad."}],
            tools=[TEST_TOOL],
            tool_choice="auto",  # the only mode vLLM supports for gpt-oss
        )
    except openai.AuthenticationError:
        print("FAIL: the server rejected LLM_API_KEY.")
        return 1
    except openai.NotFoundError:
        print("FAIL: 404. Check LLM_MODEL, and that LLM_BASE_URL ends in /v1.")
        return 1
    except openai.APITimeoutError:
        print("FAIL: timed out after 60 s. Is the Brev instance running?")
        return 1
    except openai.APIConnectionError:
        print("FAIL: couldn't connect. Check LLM_BASE_URL and that the Brev instance is up.")
        return 1
    except openai.APIStatusError as e:
        print(f"FAIL: server returned HTTP {e.status_code}.")
        return 1
    ms = round((time.perf_counter() - start) * 1000)

    message = response.choices[0].message
    print(f"Reply in {ms} ms.")
    if not message.tool_calls:
        print("FAIL: no tool_calls in the reply. The model said:")
        print(f"  {message.content!r}")
        print("If you're on vLLM, the server needs: --tool-call-parser openai --enable-auto-tool-choice")
        return 1

    for call in message.tool_calls:
        print(f"tool_call: {call.function.name}({call.function.arguments})  id={call.id}")
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
