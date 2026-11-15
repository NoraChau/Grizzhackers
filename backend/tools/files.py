"""Open folders and files: "Open my Downloads folder and open the newest PDF".

Owner: Nora

Docs:
  - pathlib: https://docs.python.org/3/library/pathlib.html  (Path.home(), .glob(), .stat().st_mtime)
  - os.startfile, which opens with the default app like a double-click:
    https://docs.python.org/3/library/os.html#os.startfile
  - winreg (where Windows says each user folder really is):
    https://docs.python.org/3/library/winreg.html
"""

import os
import winreg
from pathlib import Path

# OneDrive often moves Documents/Desktop/Pictures to ~/OneDrive/..., so ~/Documents can be
# the WRONG folder (it was on Jay's laptop). Windows records the real location in the
# registry under these value names; fall back to ~/<Name> if the lookup fails.
_SHELL_FOLDERS_KEY = r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"


def _user_folder(registry_name: str, fallback: str) -> Path:
    """Return the real path of a user folder like Documents, as Windows sees it."""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _SHELL_FOLDERS_KEY) as key:
            raw, _type = winreg.QueryValueEx(key, registry_name)
        return Path(winreg.ExpandEnvironmentStrings(raw))
    except OSError:
        return Path.home() / fallback


# Folders the model may name. Keep it to the user's own folders.
FOLDERS: dict[str, Path] = {
    "downloads": _user_folder("{374DE290-123F-4565-9164-39C4925E467B}", "Downloads"),
    "documents": _user_folder("Personal", "Documents"),
    "desktop": _user_folder("Desktop", "Desktop"),
    "pictures": _user_folder("My Pictures", "Pictures"),
}

# Only these may be opened. Never .exe, .bat, .cmd, .ps1, .lnk, .msi, ...: "open the newest
# file in Downloads" must never run a downloaded program.
SAFE_EXTENSIONS: set[str] = {
    ".pdf",
    ".txt",
    ".docx",
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".webp",
    ".mp3",
    ".mp4",
}


def open_folder(name: str) -> str:
    """Open FOLDERS[name] in File Explorer. Returns e.g. "opened downloads".

    Unknown name -> "error: ..." listing the folders you do know.
    """
    key = name.strip().lower()
    folder = FOLDERS.get(key)
    if folder is None:
        return f"error: unknown folder '{name}'. Try: {', '.join(FOLDERS)}"
    if not folder.exists():
        return f"error: the {key} folder doesn't exist on this PC."

    try:
        os.startfile(folder)
    except OSError as e:
        return f"error: couldn't open {key}: {e}"
    return f"opened {key}"


def open_newest_file(folder: str, extension: str) -> str:
    """Open the most recently modified file with `extension` in FOLDERS[folder].

    e.g. open_newest_file("downloads", ".pdf") -> "opened report.pdf".
    Refuse anything not in SAFE_EXTENSIONS. No matching file -> "error: no .pdf files in downloads".
    """
    # Accept "pdf", "PDF" and ".pdf" alike, then check against the allow-list.
    ext = "." + extension.strip().lower().lstrip(".")
    if ext not in SAFE_EXTENSIONS:
        return f"error: I can't open {ext} files. I can open: {', '.join(sorted(SAFE_EXTENSIONS))}"

    key = folder.strip().lower()
    folder_path = FOLDERS.get(key)
    if folder_path is None:
        return f"error: unknown folder '{folder}'. Try: {', '.join(FOLDERS)}"
    if not folder_path.exists():
        return f"error: the {key} folder doesn't exist on this PC."

    files = [p for p in folder_path.glob(f"*{ext}") if p.is_file()]
    newest = max(files, key=lambda p: p.stat().st_mtime, default=None)
    if newest is None:
        return f"error: no {ext} files in {key}"

    try:
        os.startfile(newest)
    except OSError as e:
        return f"error: couldn't open {newest.name}: {e}"
    return f"opened {newest.name}"
