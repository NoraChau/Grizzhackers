"""Open pages of the Windows Settings app, like Display or Bluetooth.

Owner: Sarahi

How it works: Windows has special links that start with "ms-settings:". Opening one jumps
straight to that Settings page. Try it now: press Win+R, type ms-settings:display, press Enter.

In Python, os.startfile("ms-settings:display") does the same thing.
  - os.startfile: https://docs.python.org/3/library/os.html#os.startfile
  - The full list of pages:
    https://learn.microsoft.com/en-us/windows/apps/develop/launch/launch-settings-app

Words you'll see:
  - dict: a lookup table. SETTINGS_PAGES["display"] gives back "ms-settings:display".
  - return value: what a function hands back when it's done. The AI reads it to know
    whether the action worked.
"""

# Friendly name the AI will say -> the ms-settings link.
# The AI can ONLY pick names from this list.
SETTINGS_PAGES: dict[str, str] = {
    "display": "ms-settings:display",
    "bluetooth": "ms-settings:bluetooth",
    # TODO(Sarahi): add 6-10 more pages that someone who can't use a mouse would want
    # (sound, mouse, accessibility, ...). Find them in the list linked above and test
    # each one with Win+R before adding it.
}


def open_settings(page: str) -> str:
    """Open the Settings page called `page` (one of the names in SETTINGS_PAGES).

    Return "opened display settings" if it worked, or
    "error: I don't know a settings page called 'xyz'" if `page` isn't in SETTINGS_PAGES.

    TODO(Sarahi), in small steps:
      1. Check whether `page` is in SETTINGS_PAGES. If not, return the error string.
      2. Call os.startfile(...) with the matching link. (Add `import os` at the top.)
      3. Return a short success message.
    Test it from the repo root with the venv active:
      python -c "from backend.tools.settings import open_settings; print(open_settings('display'))"
    """
    return "error: open_settings is not implemented yet"
