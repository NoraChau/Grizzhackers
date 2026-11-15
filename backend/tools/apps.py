import ctypes
import os
import time

import keyboard
from pywinauto import Desktop
from pywinauto.timings import TimeoutError as UiaTimeout

# Friendly name the model says -> (what to launch, regex for its window title).
# Only apps in this dict can be opened, and tool_schemas.py turns the keys into an enum.
# Never pass the model's text straight to a shell: that is how prompt injection runs commands.
# Deliberately NOT here: terminals (cmd, PowerShell, Windows Terminal), since type_text would
# let the model run any command, and Task Manager, which needs admin rights.
# Titles checked on Win11: Edge ends in "Microsoft​Edge" (zero-width space), so match "Edge$".
APPS: dict[str, tuple[str, str]] = {
    "notepad": ("notepad.exe", r".*Notepad$"),
    "calculator": ("calc.exe", r"^Calculator$"),
    "paint": ("mspaint.exe", r".*Paint$"),
    "snipping tool": ("SnippingTool.exe", r"^Snipping Tool$"),
    "file explorer": ("explorer.exe", r".*File Explorer$"),
    "edge": ("msedge.exe", r".*Edge$"),
    "firefox": ("firefox.exe", r".*Mozilla Firefox$"),
    "word": ("winword.exe", r"^(.* - )?Word$"),
    "excel": ("excel.exe", r"^(.* - )?Excel$"),
    "powerpoint": ("powerpnt.exe", r"^(.* - )?PowerPoint$"),
}

MASCOT_TITLE = "GrizzHelper"  # the mascot window's <title> in mascot/index.html

# The window open_app focused last. Clicking the mascot (typing a request, pressing Yes on a
# confirm) moves keyboard focus to the mascot, so type_text/press_keys re-focus this first.
# Without it, "close calculator" -> confirm -> alt+f4 closed the MASCOT.
_last_window = None


def _foreground_title() -> str:
  user32 = ctypes.windll.user32
  hwnd = user32.GetForegroundWindow()
  buf = ctypes.create_unicode_buffer(512)
  user32.GetWindowTextW(hwnd, buf, 512)
  return buf.value


def focus_last_app() -> str | None:
  """Put focus back on the app open_app last focused. Returns an error string, or None if OK."""
  win = _last_window
  if win is not None and ctypes.windll.user32.IsWindow(win.handle):
    try:
      win.set_focus()
      time.sleep(0.2)
      return None
    except Exception:  # noqa: BLE001 - window is closing: fall through to the check below
      pass
  if _foreground_title() == MASCOT_TITLE:
    return "Error: No app is focused. Use open_app first."
  return None


def _new_notepad_tab(spec) -> None:
  """Win11 Notepad restores old tabs: wait until it's ready, then start a blank tab.

  Typing while it's still restoring tabs dropped letters ("buy milk" -> "buy lllk").
  """
  try:
    doc = spec.child_window(control_type="Document", found_index=0)
    doc.wait("ready", timeout=5)
    if (not doc.wrapper_object().window_text().strip()):
      return  # already a blank tab: the model calling open_app twice mustn't pile up tabs
  except Exception:  # noqa: BLE001 - still try the new tab
    pass
  keyboard.send("ctrl+n")
  time.sleep(0.5)


def open_app(name: str) -> str:
  global _last_window
  try:
    key = name.strip().lower()

    if (not APPS.get(key)) :
      return f"Error: I don't know an app called {name}."

    target, title_pattern = APPS[key]
    desk = Desktop(backend="uia")
    spec = desk.window(title_re=title_pattern, control_type="Window", found_index=0)

    if (spec.exists()):
      try:
        spec.wait("visible", timeout=10)
      except UiaTimeout:
        pass
      _last_window = spec.wrapper_object()
      _last_window.set_focus()
      if (key == "notepad"):
        _new_notepad_tab(spec)
        return "notepad was already open, now on a blank tab."
      return f"{key} was already open, focused the window."

    try:
      # os.startfile = "Run" box / double-click. Unlike subprocess.Popen it also finds apps
      # registered under "App Paths" (Edge, Firefox, Office), which aren't on PATH.
      os.startfile(target)
    except OSError as e:
      return f"Error: Couldn't launch {name}: {e}"

    try:
      spec.wait("visible", timeout=10)
    except UiaTimeout:
      return f"Error: Started {name}, but its window never appeared."

    _last_window = spec.wrapper_object()
    _last_window.set_focus()
    if (key == "notepad"):
      _new_notepad_tab(spec)
      return "Opened notepad on a blank tab."

    return f"Opened {key}"

  except Exception as e:  # noqa: BLE001
    return f"Error: open_app failed: {e}"
