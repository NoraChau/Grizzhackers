"""Tools: raw keyboard and mouse (pyautogui). Fallback when ui.py can't find a control.

Owner: Jay
Docs: https://pyautogui.readthedocs.io/en/latest/

Gotchas:
- Keep pyautogui's FAILSAFE on (slam the mouse into a screen corner to abort). Mention it in the demo.
- Display scaling (125%, 150%) can make screenshot pixels differ from click coordinates.
  Test on the demo laptop.
- These act on whatever window has focus. Focus the right window first (apps.focus_window).
"""


def type_text(text: str) -> str:
    """Type text into whatever window has focus.

    TODO(exp1)
    """
    raise NotImplementedError("TODO(exp1): type_text")


def press_keys(keys: list[str]) -> str:
    """Press a key combination together, e.g. ["ctrl", "s"].

    Some combos are destructive (ctrl+w, alt+f4). Check them in agent/safety.py.
    TODO(exp1)
    """
    raise NotImplementedError("TODO(exp1): press_keys")


def click_at(x: int, y: int) -> str:
    """Click at screen coordinates. Last resort, after ui.click_control fails.

    TODO(exp1)
    """
    raise NotImplementedError("TODO(exp1): click_at")
