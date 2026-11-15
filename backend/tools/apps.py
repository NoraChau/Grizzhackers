import os
import subprocess
from pathlib import Path

from pywinauto import Desktop
from pywinauto.timings import TimeoutError as UiaTimeout

# Friendly name the model says -> what to launch. Only apps in this dict can be opened.
# Never pass the model's text straight to a shell: that is how prompt injection runs commands.
APPS: dict[str, tuple[str, str]] = {
    "notepad": ("notepad.exe", r".*Notepad$"),
}

def open_app(name: str) -> str:
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
      spec.wrapper_object().set_focus()
      return f"{name} was already open, focused the window."

    try:
      path = Path(target)
      if (path.is_file() or path.is_dir()):
        os.startfile(target)
      else:
        subprocess.Popen([target])

    except OSError as e:
      return f"Error: Couldn't launch {name}: {e}"

    try:
      spec.wait("visible", timeout=10)
    except UiaTimeout:
      return f"Error: Started {name}, but its window never appeared."

    win = spec.wrapper_object()
    win.set_focus()

    return f"Opened {name}"

  except Exception as e:  # noqa: BLE001
    return f"Error: open_app failed: {e}"
