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

from backend.tools import apps

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

# TODO(Jay):    CLICK_CONTROL    -> ui.click_control
# TODO(Jay):    TYPE_TEXT        -> keyboard_mouse.type_text
# TODO(Jay):    PRESS_KEYS       -> keyboard_mouse.press_keys
# TODO(Nora):   DESCRIBE_SCREEN  -> screen.describe_screen
# TODO(Nora):   OPEN_FOLDER      -> files.open_folder
# TODO(Nora):   OPEN_NEWEST_FILE -> files.open_newest_file
# TODO(Sarahi): OPEN_SETTINGS    -> settings.open_settings  (hint: "enum": list(settings.SETTINGS_PAGES))
# TODO(Nora):   WEB_SEARCH       -> web.web_search. Only add it to TOOLS when EXA_API_KEY is set,
#               and keep the total at 8 or fewer.

TOOLS: list[dict[str, Any]] = [OPEN_APP]

# The loop looks up the Python function by the name the model sent back.
TOOL_FUNCTIONS: dict[str, Callable[..., str]] = {
    "open_app": apps.open_app,
}
