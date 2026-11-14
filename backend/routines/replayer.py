"""Replay a recorded routine ("do my study setup").

Owner: Nora
"""

from typing import Any


def replay(steps: list[dict[str, Any]]) -> str:
    """Run recorded steps in order using the same tools the agent uses. Return a short summary.

    TODO(Nora):
    - Wait for each window to be ready before the next step (apps open slowly).
    - Stop at the first failed step and say which one failed.
    - Destructive steps still go through agent/safety.py. Replays don't skip confirmation.
    """
    raise NotImplementedError("TODO(Nora): replay")
