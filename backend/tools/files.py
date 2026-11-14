"""Tools: save, read, and delete text notes.

Owner: UNASSIGNED (not in CLAUDE.md's ownership table yet; decide as a team)

Security: the model chooses the note name. Keep every file inside NOTES_DIR and reject names
with "..", "/" or "\\" so a bad instruction can't write or delete files elsewhere on the computer.
"""

from pathlib import Path

NOTES_DIR = Path.home() / "Documents" / "Companion Notes"


def save_note(title: str, text: str) -> str:
    """Save `text` to NOTES_DIR/<title>.txt (create the folder if needed). Return where it was saved.

    TODO(unassigned)
    """
    raise NotImplementedError("TODO(unassigned): save_note")


def read_note(title: str) -> str:
    """Return the text of a saved note, or a short message if it doesn't exist.

    TODO(unassigned)
    """
    raise NotImplementedError("TODO(unassigned): read_note")


def delete_note(title: str) -> str:
    """Delete a saved note.

    DESTRUCTIVE: listed in agent/safety.py DESTRUCTIVE_TOOLS, so the user confirms first.
    TODO(unassigned)
    """
    raise NotImplementedError("TODO(unassigned): delete_note")
