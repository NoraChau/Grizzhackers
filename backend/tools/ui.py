"""Tools: work with controls inside a window by name, using Windows UI Automation (pywinauto).

This is the preferred way to act: find a button by its name, not by pixel position.
Fallbacks, in order: keyboard_mouse.py (pyautogui), then screen.py (Gemini vision).

Owner: Jay
Docs: https://pywinauto.readthedocs.io/en/latest/ (backend="uia")
Tip: the "Accessibility Insights for Windows" app or pywinauto's print_control_identifiers()
shows the names and control types you can search for.
"""


def read_window(window_title: str) -> str:
    """List the clickable / typeable controls in a window (name + control type), one per line.

    The model calls this to "look" at a window before clicking. Keep the output short:
    skip unnamed controls and cap the number of lines.
    TODO(exp1)
    """
    raise NotImplementedError("TODO(exp1): read_window")


def click_control(window_title: str, control_name: str) -> str:
    """Click a button, menu item, or tab by its visible name.

    TODO(exp1)
    """
    raise NotImplementedError("TODO(exp1): click_control")


def type_into(window_title: str, text: str) -> str:
    """Type text into the main text box of a window (e.g. Notepad's editor).

    TODO(exp1)
    """
    raise NotImplementedError("TODO(exp1): type_into")
