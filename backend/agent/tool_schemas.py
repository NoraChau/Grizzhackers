"""JSON schemas for the tools gpt-oss can call, plus the name -> Python function lookup.

Owner: Jay. Each tool's owner writes the schema for their tool and adds it here in their PR.

Rules (vLLM + gpt-oss are picky):
  - 6-8 tools in TOOLS, total. More tools = a more confused model.
  - One-sentence descriptions that say WHEN to use the tool.
  - Tight schemas: list every argument in "required", set "additionalProperties": False,
    and use "enum" whenever there is a fixed set of choices.
  - The loop must use tool_choice="auto" (the only mode vLLM supports for gpt-oss).

Schema format: https://platform.openai.com/docs/guides/function-calling
"""

from collections.abc import Callable
from typing import Any

from openai.types.chat import ChatCompletionFunctionToolParam

from backend.tools import apps

TOOLS: list[ChatCompletionFunctionToolParam] = [
    {
        "type": "function",
        "function": {
            "name": "open_app",
            "description": "Open a Windows app by name.",
            "parameters": {
                "type": "object",
                "properties": {"name": {"type": "string", "description": "notepad, calculator, ..."}},
                "required": ["name"],
            },
        },
    },
]

# Example: copy this shape for every other tool.
OPEN_APP: dict[str, Any] = {
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

# The loop looks up the Python function by the name the model sent back.
TOOL_FUNCTIONS: dict[str, Callable[..., str]] = {
    "open_app": apps.open_app,
}
