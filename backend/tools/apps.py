"""Tools: open, focus, list, and close desktop apps.

Owner: Experienced #1
Docs: https://pywinauto.readthedocs.io/en/latest/getting_started.html (use backend="uia")
"""


def open_app(name: str) -> str:
    """Start an app by friendly name ("notepad", "calculator") and wait until its window is ready.

    Returns e.g. "Opened Notepad" or "I don't know an app called 'xyz'".

    TODO(exp1):
    - Map friendly names to what to launch.
    - Windows 11 gotcha: Calculator and the new Notepad are Store apps. The process you start
      can hand off to another process and exit, so find the window by its title instead of
      trusting the process id you started.
    """
    raise NotImplementedError("TODO(exp1): open_app")


def focus_window(title: str) -> str:
    """Bring the window whose title contains `title` to the front.

    TODO(exp1)
    """
    raise NotImplementedError("TODO(exp1): focus_window")


def list_windows() -> str:
    """Return the titles of visible top-level windows, one per line (helps the model pick one).

    TODO(exp1)
    """
    raise NotImplementedError("TODO(exp1): list_windows")


def close_app(title: str) -> str:
    """Close the window whose title contains `title`.

    DESTRUCTIVE: may lose unsaved work, so it is listed in agent/safety.py DESTRUCTIVE_TOOLS.
    TODO(exp1)
    """
    raise NotImplementedError("TODO(exp1): close_app")
