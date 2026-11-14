"""Record a routine by watching the user once (hero task 4, "watch me").

Owner: Nora

Design idea: record *what* happened (which app opened, which window and control was clicked,
what text was typed), not raw x/y pixels. Pixel positions break as soon as a window moves.
Each step should map onto a tool the agent already has (apps.open_app, ui.click_control, ...),
so replaying is just calling those tools again.

Privacy: a recorder sees every keystroke, passwords included. Only record between explicit
start/stop, keep the overlay in the "recording" state the whole time, and skip password fields.
"""

from typing import Any


def start_recording(name: str) -> str:
    """Start watching the user's actions for a routine called `name`. Returns a short status.

    TODO(Nora)
    """
    raise NotImplementedError("TODO(Nora): start_recording")


def stop_recording() -> list[dict[str, Any]]:
    """Stop watching and return the recorded steps (save them with memory.store.save_routine).

    TODO(Nora): decide the step format first and share it with Jay.
    """
    raise NotImplementedError("TODO(Nora): stop_recording")
