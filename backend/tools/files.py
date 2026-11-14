"""Open folders and files: "Open my Downloads folder and open the newest PDF".

Owner: Nora

Docs:
  - pathlib: https://docs.python.org/3/library/pathlib.html  (Path.home(), .glob(), .stat().st_mtime)
  - os.startfile, which opens with the default app like a double-click:
    https://docs.python.org/3/library/os.html#os.startfile
"""

from pathlib import Path

# Folders the model may name. Keep it to the user's own folders.
# Gotcha: OneDrive often moves Documents/Desktop/Pictures to ~/OneDrive/...; check each laptop.
FOLDERS: dict[str, Path] = {
    "downloads": Path.home() / "Downloads",
    # TODO(Nora): documents, desktop, pictures
}

# Only these may be opened. Never .exe, .bat, .cmd, .ps1, .lnk, .msi, ...: "open the newest
# file in Downloads" must never run a downloaded program.
SAFE_EXTENSIONS: set[str] = {".pdf", ".txt"}  # TODO(Nora): add images, .docx, ...


def open_folder(name: str) -> str:
    """Open FOLDERS[name] in File Explorer. Returns e.g. "opened Downloads".

    TODO(Nora): implement. Unknown name -> "error: ..." listing the folders you do know.
    """
    return "error: open_folder is not implemented yet"


def open_newest_file(folder: str, extension: str) -> str:
    """Open the most recently modified file with `extension` in FOLDERS[folder].

    e.g. open_newest_file("downloads", ".pdf") -> "opened report.pdf".
    Refuse anything not in SAFE_EXTENSIONS. No matching file -> "error: no PDF files in Downloads".

    TODO(Nora): implement.
    """
    return "error: open_newest_file is not implemented yet"
