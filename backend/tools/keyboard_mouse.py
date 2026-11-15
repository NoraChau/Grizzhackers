"""Type text, press shortcuts, click coordinates: the fallback when UIA can't do it.

Owner: Jay

Docs:
  - pyautogui 0.9.54: https://pyautogui.readthedocs.io/en/latest/  (hotkey, write, click)
  - keyboard 0.13.5: https://github.com/boppreh/keyboard  (write handles non-English characters)
"""
import time

import keyboard
import pyautogui

MAX_CHARS = 2000

def normalize_keys(keys: str) -> str:
    return keys.lower().replace(" ", "")

def type_text(text: str) -> str:
    try:
        if (not text):
            return "Error: Nothing to type"
        if (len(text) > MAX_CHARS):
            return "Error: Text is too long (Max 2000 characters)"
        time.sleep(0.5)

        keyboard.write(text, delay=0.01)
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
