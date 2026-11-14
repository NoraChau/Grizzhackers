"""Click buttons and menus by name with Windows UI Automation (UIA).

Owner: Jay

UIA is the accessibility API screen readers use. Every control has a name ("Save"), a
control type ("Button"), and a parent window. Far more reliable than clicking pixels.

Order of attempts (CLAUDE.md): pywinauto UIA first -> keyboard_mouse fallback ->
Gemini vision (screen.locate_on_screen) as the last resort.

Docs (pywinauto 0.6.9): https://pywinauto.readthedocs.io/en/latest/getting_started.html
  - Desktop(backend="uia").window(title_re=...) finds a top-level window
  - .child_window(title=..., control_type=...) finds a control inside it; .click_input() clicks
  - .print_control_identifiers() dumps every control: use it while developing to learn names
Tip: Accessibility Insights for Windows (free, from Microsoft) shows the UIA name of
whatever you hover: https://accessibilityinsights.io/docs/windows/overview/
"""


def click_control(name: str, control_type: str = "", window_title: str = "") -> str:
    """Click the control called `name` (e.g. "File", "Save") in a window.

    window_title: part of the window's title, e.g. "Notepad". Empty = the window in front.
    control_type: narrows the search: "Button", "MenuItem", "Edit", "ListItem", "TabItem", ...

    If UIA can't find it, fall back to screen.locate_on_screen(name) and
    keyboard_mouse.click_at(x, y).
    Returns e.g. "clicked 'Save' (Button)" or "error: no control named 'Save' in Notepad".

    TODO(Jay): implement.
    """
    return "error: click_control is not implemented yet"
