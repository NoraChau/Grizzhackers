"""Open folders and files: "Open my Downloads folder and open the newest PDF" / "...my resume".

Owner: Nora

Docs:
  - pathlib: https://docs.python.org/3/library/pathlib.html  (Path.home(), .glob(), .stat().st_mtime)
  - os.startfile, which opens with the default app like a double-click:
    https://docs.python.org/3/library/os.html#os.startfile
  - winreg (where Windows says each user folder really is):
    https://docs.python.org/3/library/winreg.html
"""

import difflib
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
    ".md",
    ".xlsx",
    ".pptx",
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


def _simplify(text: str) -> str:
    """'Resume-J-sV3.pdf' -> 'resumejsv3pdf': ignore case, spaces and punctuation."""
    return "".join(ch for ch in text.lower() if ch.isalnum())


def open_file(folder: str, name: str, extension: str) -> str:
    """Open a file in FOLDERS[folder]: the newest one whose name contains `name`.

    name "" = any name, so ("downloads", "", ".pdf") opens the newest PDF.
    extension "any" = any type in SAFE_EXTENSIONS (people often don't know the type).
    Names match loosely because speech-to-text rarely gets punctuation right.
    Refuse anything not in SAFE_EXTENSIONS. No match -> "error: ..." with close names.
    """
    # Accept "pdf", "PDF" and ".pdf" alike, then check against the allow-list.
    ext = extension.strip().lower()
    if ext == "any":
        allowed = SAFE_EXTENSIONS
    else:
        ext = "." + ext.lstrip(".")
        if ext not in SAFE_EXTENSIONS:
            return f"error: I can't open {ext} files. I can open: {', '.join(sorted(SAFE_EXTENSIONS))}"
        allowed = {ext}

    key = folder.strip().lower()
    folder_path = FOLDERS.get(key)
    if folder_path is None:
        return f"error: unknown folder '{folder}'. Try: {', '.join(FOLDERS)}"
    if not folder_path.exists():
        return f"error: the {key} folder doesn't exist on this PC."

    candidates = [p for p in folder_path.iterdir() if p.is_file() and p.suffix.lower() in allowed]
    wanted = _simplify(name)
    matches = [p for p in candidates if wanted in _simplify(p.name)]
    if not matches:
        if not wanted:
            return f"error: no {ext if ext != 'any' else 'openable'} files in {key}"
        by_simple = {_simplify(p.stem): p.name for p in candidates}
        close = difflib.get_close_matches(wanted, by_simple, n=3, cutoff=0.5)
        hint = f" Did you mean: {', '.join(by_simple[c] for c in close)}?" if close else ""
        return f"error: no file named like '{name}' in {key}.{hint}"

    newest = max(matches, key=lambda p: p.stat().st_mtime)
    try:
        os.startfile(newest)
    except OSError as e:
        return f"error: couldn't open {newest.name}: {e}"
    if wanted and len(matches) > 1:
        return f"opened {newest.name} (the newest of {len(matches)} matching files)"
    return f"opened {newest.name}"
