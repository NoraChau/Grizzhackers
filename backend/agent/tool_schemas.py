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

from openai.types.chat import ChatCompletionFunctionToolParam

from backend.tools import apps, files, keyboard_mouse, screen

TOOLS: list[ChatCompletionFunctionToolParam] = [
    {
        "type": "function",
        "function": {
            "name": "open_app",
            "description": "Open a Windows app by name, or focus it if it's already open. Notepad always gets a new blank tab.",
            "parameters": {
                "type": "object",
                "properties": {"name": {"type": "string", "enum": list(apps.APPS)}},
                "required": ["name"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "type_text",
            "description": "Type text into the app that is currently focused. Open or focus the app first.",
            "parameters": {
                "type": "object",
                "properties": {"text": {"type": "string", "description": "The exact text to type."}},
                "required": ["text"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "press_keys",
            "description": "Press one keyboard shortcut in the focused app.",
            "parameters": {
                "type": "object",
                "properties": {"keys": {"type": "string", "description": "One shortcut like ctrl+s or enter."}},
                "required": ["keys"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "describe_screen",
            "description": "Look at the screen and answer a question about it. Use when the user asks what's on screen.",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {"type": "string", "description": "What the user wants to know, e.g. What's on my screen?"},
                },
                "required": ["question"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "open_folder",
            "description": "Open one of the user's folders in File Explorer.",
            "parameters": {
                "type": "object",
                "properties": {"name": {"type": "string", "enum": list(files.FOLDERS)}},
                "required": ["name"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "open_file",
            "description": "Open a file in one of the user's folders, by part of its name, or the newest one if no name is given.",
            "parameters": {
                "type": "object",
                "properties": {
                    "folder": {"type": "string", "enum": list(files.FOLDERS)},
                    "name": {"type": "string", "description": "Part of the file name the user said, or \"\" for the newest file."},
                    "extension": {"type": "string", "enum": ["any", *sorted(files.SAFE_EXTENSIONS)]},
                },
                "required": ["folder", "name", "extension"],
                "additionalProperties": False,
            },
        },
    },
]

# The loop looks up the Python function by the name the model sent back.
TOOL_FUNCTIONS: dict[str, Callable[..., str]] = {
    "open_app": apps.open_app,
    "type_text": keyboard_mouse.type_text,
    "press_keys": keyboard_mouse.press_keys,
    "describe_screen": screen.describe_screen,
    "open_folder": files.open_folder,
    "open_file": files.open_file,
}
