"""Type text, press shortcuts, click coordinates: the fallback when UIA can't do it.

Owner: Jay

Docs:
  - pyautogui 0.9.54: https://pyautogui.readthedocs.io/en/latest/  (hotkey, write, click)
  - keyboard 0.13.5: https://github.com/boppreh/keyboard  (write handles non-English characters)
"""
import time

import keyboard
import pyautogui
import win32clipboard
import win32con

from backend.tools.apps import focus_last_app

MAX_CHARS = 2000

def normalize_keys(keys: str) -> str:
    return keys.lower().replace(" ", "")

def _get_clipboard_text() -> str | None:
    win32clipboard.OpenClipboard()
    try:
        if win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
            return win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
        return None
    finally:
        win32clipboard.CloseClipboard()


def _set_clipboard_text(text: str) -> None:
    win32clipboard.OpenClipboard()
    try:
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, text)
    finally:
        win32clipboard.CloseClipboard()


def _paste(text: str) -> None:
    """Type `text` by pasting it, then put the user's clipboard text back.

    Why not keyboard.write: the server's F9 push-to-talk hook runs in this same process, and
    with it active, fast key-by-key typing drops letters ("GrizzHelper" -> "rrrr").
    One Ctrl+V can't drop letters, and handles any Unicode. (Non-text clipboard
    contents, like a copied image, are not restored.)
    """
    previous = _get_clipboard_text()
    _set_clipboard_text(text)
    keyboard.send("ctrl+v")
    time.sleep(0.3)  # let the app read the clipboard before we restore it
    if previous is not None:
        _set_clipboard_text(previous)


def type_text(text: str) -> str:
    try:
        if (not text):
            return "Error: Nothing to type"
        if (len(text) > MAX_CHARS):
            return "Error: Text is too long (Max 2000 characters)"
        if (error := focus_last_app()):  # the mascot may have taken focus
            return error
        time.sleep(0.3)

        try:
            _paste(text)
        except Exception:  # noqa: BLE001 - clipboard busy: type slowly instead (30 ms+ is reliable)
            keyboard.write(text, delay=0.05)
        return f"Typed {len(text)} characters"
    except Exception as e:  # noqa: BLE001
        return f"Error: Typing failed: {e}"


def press_keys(keys: str) -> str:
    try:
        combo = normalize_keys(keys)
        if (not combo):
            return "Error: No keys given"
        if ("," in combo):
            return "Error: One short-cut at a time"
        if (error := focus_last_app()):  # e.g. pressing Yes on a confirm focused the mascot
            return error
        keyboard.send(combo)
        return f"Pressed {combo}"
    except ValueError as e:
      return f"Error: Unknown key in '{keys}': {e}"
    except Exception as e:  # noqa: BLE001
        return f"Error: press_keys failed: {e}"

def click_at(x: int, y: int) -> str:
    try:
        width, height = pyautogui.size()
        if not (0 <= x < width and 0 <= y < height):
            return f"Error: ({x}, {y}) is off screen (screen is {width}x{height})"
        pyautogui.click(x, y)
        return f"Clicked at ({x}, {y})"
    except pyautogui.FailSafeException:
        return "Error: Click cancelled"
    except Exception as e:  # noqa: BLE001
        return f"Error: Click failed: {e}"
