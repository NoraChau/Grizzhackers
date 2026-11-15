import os

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
      # os.startfile = "Run" box / double-click. Unlike subprocess.Popen it also finds apps
      # registered under "App Paths" (Edge, Firefox, Office), which aren't on PATH.
      os.startfile(target)
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
