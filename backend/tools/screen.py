"""Screenshots + Gemini vision: "What's on my screen?" and finding controls UIA can't see.

Owner: Nora

Last resort only: try UIA (tools/ui.py) first. The free tier is rate-limited, so don't send
a screenshot on every step, and retry HTTP 429 a few times with backoff
(google.genai.errors.ClientError has the status code).

Docs:
  - mss 10.2: https://python-mss.readthedocs.io/  (mss.mss().grab(...), mss.tools.to_png)
  - google-genai 3.3 SDK: https://googleapis.github.io/python-genai/
  - Image understanding, incl. bounding boxes: https://ai.google.dev/gemini-api/docs/image-understanding
The model name comes from GEMINI_VISION_MODEL. Check the docs for current names; don't guess.
"""

import mss.tools
from google import genai
from mss import MSS

MAX_RETRIES = 3

_client: genai.Client | None = None  # the ONE shared client; see get_gemini_client()


def get_gemini_client() -> genai.Client:
    """Return the shared genai.Client(), creating it the first time it's needed.

    genai.Client() reads GEMINI_API_KEY from the environment by itself.

    TODO(Nora): implement.
    """
    global _client
    if _client is None:
        _client = genai.Client()
    return _client
    raise NotImplementedError("TODO(Nora): get_gemini_client")


def take_screenshot() -> bytes:
    """Capture the main monitor and return it as PNG bytes.

    mss gotcha: sct.monitors[1] is the primary monitor; sct.monitors[0] is all monitors
    stitched together.

    TODO(Nora): implement.
    """
    with MSS() as sct:
        img = sct.grab(sct.monitors[1])
        png_bytes = mss.tools.to_png(img.rgb, img.size)
    if png_bytes is None:
        raise RuntimeError("to_png returned None")
    return png_bytes
    raise NotImplementedError("TODO(Nora): take_screenshot")


def describe_screen(question: str = "What's on my screen?") -> str:
    """Tool: screenshot -> Gemini -> a short plain-English answer.

    Ask Gemini for 2-3 sentences: the answer is shown in the bubble and spoken aloud.
    On failure return "error: ..." (e.g. "error: vision is rate-limited, try again in a minute").

    TODO(Nora): implement.
    """
    return "error: describe_screen is not implemented yet"


def locate_on_screen(description: str) -> tuple[int, int] | None:
    """Helper for ui.click_control (not a model tool): find `description` on screen.

    e.g. "the Save button". Returns the center of it in screen pixels, or None if Gemini
    can't find it. Gemini can return a bounding box: check the image-understanding docs for
    its coordinate format, then convert to real pixels using the screenshot's size.

    TODO(Nora): implement.
    """
    raise NotImplementedError("TODO(Nora): locate_on_screen")
