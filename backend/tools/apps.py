"""Open Windows apps.

Owner: Jay

Docs:
  - pywinauto 0.6.9: https://pywinauto.readthedocs.io/en/latest/
  - subprocess: https://docs.python.org/3/library/subprocess.html
"""

# Friendly name the model says -> what to launch. Only apps in this dict can be opened.
# Never pass the model's text straight to a shell: that is how prompt injection runs commands.
APPS: dict[str, str] = {
    "notepad": "notepad.exe",
    # TODO(Jay): calculator, file explorer, paint, ...
}


def open_app(name: str) -> str:
    """Open the app called `name` (e.g. "notepad") and wait until its window is visible.

    Returns a short result for the model, e.g. "opened Notepad", or
    "error: I don't know an app called 'xyz'".

    Windows 11 gotcha: notepad.exe and calc.exe start a stub process that hands off to the
    Store version of the app and exits, so pywinauto's Application().start(...) loses track
    of the window. Launch the exe, then find the window separately with
    Desktop(backend="uia").window(title_re=...) and .wait("visible", timeout=10).

    TODO(Jay): implement.
    """
    return "error: open_app is not implemented yet"
