"""MongoDB Atlas storage.

Owner: Intermediate
Docs: https://www.mongodb.com/docs/languages/python/pymongo-driver/current/

Suggested collections (one database, e.g. "companion"):
    commands     {text, steps, ok, created_at}
    routines     {name, steps, created_at}
    preferences  {key, value}

Gotchas:
- MONGODB_URI contains a password. Never log or print it.
- Atlas blocks unknown IP addresses (Network Access). Venue Wi-Fi IPs change; add the
  current one when the connection times out.
- If Atlas is down, log a warning and keep going. The companion must still work without memory.
"""

from typing import Any


def get_db() -> Any:
    """Connect once using MONGODB_URI and return the database object.

    Create the client one time and reuse it (it holds a pool of connections).
    TODO(intermediate)
    """
    raise NotImplementedError("TODO(intermediate): get_db")


def log_command(text: str, steps: list[dict[str, Any]], ok: bool) -> None:
    """Save one finished command and the tool steps it took.

    TODO(intermediate)
    """
    raise NotImplementedError("TODO(intermediate): log_command")


def save_routine(name: str, steps: list[dict[str, Any]]) -> None:
    """Save (or replace) a recorded routine under `name`, e.g. "study setup".

    TODO(intermediate)
    """
    raise NotImplementedError("TODO(intermediate): save_routine")


def get_routine(name: str) -> list[dict[str, Any]] | None:
    """Return a routine's steps, or None if there is no routine with that name.

    TODO(intermediate)
    """
    raise NotImplementedError("TODO(intermediate): get_routine")


def get_preference(key: str, default: str | None = None) -> str | None:
    """Return a saved preference (e.g. "voice_speed"), or `default` if it's not set.

    TODO(intermediate)
    """
    raise NotImplementedError("TODO(intermediate): get_preference")


def set_preference(key: str, value: str) -> None:
    """Save a preference.

    TODO(intermediate)
    """
    raise NotImplementedError("TODO(intermediate): set_preference")
