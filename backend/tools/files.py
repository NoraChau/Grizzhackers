"""Open folders and files: "Open my Downloads folder and open the newest PDF".

Owner: Nora

Docs:
  - pathlib: https://docs.python.org/3/library/pathlib.html  (Path.home(), .glob(), .stat().st_mtime)
  - os.startfile, which opens with the default app like a double-click:
    https://docs.python.org/3/library/os.html#os.startfile
"""

import os
from pathlib import Path

# Folders the model may name. Keep it to the user's own folders.
# Gotcha: OneDrive often moves Documents/Desktop/Pictures to ~/OneDrive/...; check each laptop.
FOLDERS: dict[str, Path] = {
    "downloads": Path.home() / "Downloads",
    "documents": Path.home() / "Documents",
    "desktop": Path.home() / "Desktop",
    "pictures": Path.home() / "Pictures",
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


"""
Open FOLDERS[name] in File Explorer. Returns e.g. "opened Downloads".

Unknown name -> "error: ..." listing the folders you do know.
"""
def open_folder(name: str) -> str:

    folder = FOLDERS.get(name.strip().lower())

    if folder is None:
        return f"error: unknown folder '{name}'. Try: {', '.join(FOLDERS)}"

    if not folder.exists():
        return f"error: {folder} doesn't exist on this PC."

    os.startfile(folder)

    return f"opened {name}"


"""Open the most recently modified file with `extension` in FOLDERS[folder].

e.g. open_newest_file("downloads", ".pdf") -> "opened report.pdf".
Refuse anything not in SAFE_EXTENSIONS. No matching file -> "error: no PDF files in Downloads".
"""
def open_newest_file(folder: str, extension: str) -> str:
    # Extension filter
    if extension not in SAFE_EXTENSIONS:
        return (
            f"error: {extension} considered unsafe. Try: {', '.join(SAFE_EXTENSIONS)}"
        )

    # Get and check folder's validity
    folder_path = FOLDERS.get(folder)
    if folder_path is None:
        return f"error: unknown folder '{folder}'. Try: {', '.join(FOLDERS)}"
    if not folder_path.exists():
        return f"error: {folder_path} doesn't exist on this PC."

    files = [p for p in folder_path.glob(f"*{extension}") if p.is_file()]  # populate the list with
    newest = max(files, key=lambda p: p.stat().st_mtime, default=None)
    if newest is None:
        return f"error: no files matching '{extension}' in {folder_path}"

    os.startfile(newest)
    return f"opened {newest.name}"
