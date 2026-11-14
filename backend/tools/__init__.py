"""Tool registry: the list of tools the agent is allowed to call.

The agent needs two things per tool:
1. A JSON schema (name, description, parameters) to send to OpenAI.
2. The Python function to run when the model asks for that tool.

Every tool is a small function that returns a short string the model can read,
e.g. "Opened Notepad" or "No window titled 'Chrome' found". Errors are strings too: don't
crash the loop; tell the model what went wrong so it can try something else.

Owner: Experienced #1
Docs: https://platform.openai.com/docs/guides/function-calling
"""

from collections.abc import Callable

# TODO(exp1): fill these in as tools start working. For 4 PM you only need
# open_app (apps.py) and one way to type (ui.type_into or keyboard_mouse.type_text).
TOOL_SCHEMAS: list[dict] = []
TOOL_FUNCTIONS: dict[str, Callable[..., str]] = {}
