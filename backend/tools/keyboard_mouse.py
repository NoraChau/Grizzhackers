"""Type text, press shortcuts, click coordinates: the fallback when UIA can't do it.

Owner: Jay

Docs:
  - pyautogui 0.9.54: https://pyautogui.readthedocs.io/en/latest/  (hotkey, write, click)
  - keyboard 0.13.5: https://github.com/boppreh/keyboard  (write handles non-English characters)
"""


def type_text(text: str) -> str:
    """Type `text` into whatever has keyboard focus. Returns e.g. "typed 12 characters".

    Gotchas:
      - pyautogui.write() only types keys on a US keyboard (no é, ñ, emoji).
        keyboard.write() handles Unicode.
      - If you use pywinauto's type_keys() instead, the characters + ^ % ~ ( ) { } are
        special keys there. Escape them or the text comes out wrong.

    TODO(Jay): implement.
    """
    return "error: type_text is not implemented yet"


def press_keys(keys: str) -> str:
    """Press a shortcut like "ctrl+s", "alt+tab", or "enter". Returns e.g. "pressed ctrl+s".

    Destructive shortcuts (alt+f4, ctrl+w, ctrl+enter to send) must pass the loop's
    needs_confirmation() check first.

    TODO(Jay): implement.
    """
    return "error: press_keys is not implemented yet"


def click_at(x: int, y: int) -> str:
    """Left-click the screen at pixel (x, y). Used by the vision fallback, not a model tool.

    Keep pyautogui.FAILSAFE on (moving the mouse into a corner aborts); catch
    pyautogui.FailSafeException and return "error: ...".
    Display scaling (125%, 150%) can make screenshot pixels differ from click pixels:
    test on a laptop with scaling turned on.

    TODO(Jay): implement.
    """
    return "error: click_at is not implemented yet"
