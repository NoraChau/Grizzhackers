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

import json
import os

import mss.tools
from google import genai
from google.genai import errors, types
from mss import MSS

MAX_RETRIES = 3

_client: genai.Client | None = None  # the ONE shared client; see get_gemini_client()


"""
Return the shared genai.Client(), creating it the first time it's needed.

genai.Client() reads GEMINI_API_KEY from the environment by itself.
"""


def get_gemini_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client()
    return _client


"""
Capture the main monitor and return it as PNG bytes.

mss gotcha: sct.monitors[1] is the primary monitor; sct.monitors[0] is all monitors
stitched together.
"""


def take_screenshot() -> bytes:

    with MSS() as sct:
        img = sct.grab(sct.monitors[1])
        png_bytes = mss.tools.to_png(img.rgb, img.size)

    if png_bytes is None:
        raise RuntimeError("to_png returned None")
    # to_png() returns None when last argument is "output=" so
    # this block is mandatory to enforce function's byte return type

    return png_bytes


"""
Tool: screenshot -> Gemini -> a short plain-English answer.

Ask Gemini for 2-3 sentences: the answer is shown in the bubble and spoken aloud.
On failure return "error: ..." (e.g. "error: vision is rate-limited, try again in a minute").
"""


def describe_screen(question: str = "What's on my screen?") -> str:
    try:
        png_bytes = take_screenshot()
        # Ask J if he wants straight plain text or JSON return
        json_response = get_gemini_client().models.generate_content(
            model=os.environ["GEMINI_VISION_MODEL"],
            contents=[
                types.Part.from_bytes(data=png_bytes, mime_type="image/png"),
                question,
            ],
        )
        return json_response.text or ""
    except errors.APIError as e:
        if e.code == 429:
            return "error: vision is rate-limited, try again in a minute"
        return f"error: vision failed ({e.code})"
    except Exception as e:
        return f"error: {e}"


"""
Helper for ui.click_control (not a model tool): find `description` on screen.

e.g. "the Save button". Returns the center of it in screen pixels, or None if Gemini
can't find it. Gemini can return a bounding box: check the image-understanding docs for
its coordinate format, then convert to real pixels using the screenshot's size.
"""


def locate_on_screen(description: str) -> tuple[int, int] | None:

    try:
        png_bytes = take_screenshot()
        with MSS() as sct:
            monitor = sct.monitors[1]

        prompt = (
            f"The target is {description}. Find it on this screen. Ignore the bear mascot"
            'Reply only with JSON: {"box_2d": [y_min, x_min, y_max, x_max]} noralized to 0-1000, '
            'or {"box_2d": null} if it is not visible'
        )
        response = get_gemini_client().models.generate_content(
            model=os.environ["GEMINI_VISION_MODEL"],
            contents=[
                types.Part.from_bytes(data=png_bytes, mime_type="image/png"),
                prompt,
            ],
            config=types.GenerateContentConfig(response_mime_type="application/json"),
        )

        box = json.loads(response.text or "{}").get("point")
        if not box:
            return None

        # Central pixel of the bounding box
        y_min, x_min, y_max, x_max = box
        center_x = (x_min + x_max) / 2
        center_y = (y_min + y_max) / 2

        pixel_x = monitor["left"] + center_x / 1000 * monitor["width"]
        pixel_y = monitor["top"] + center_y / 1000 * monitor["height"]

        return int(pixel_x), int(pixel_y)

    # Catching errors
    except errors.APIError as e:
        if e.code == 429:
            raise RuntimeError("error: vision is rate-limited, try again in a minute")
        raise RuntimeError("error: vision failed ({e})")
    except (json.JSONDecodeError, ValueError, TypeError):
        raise RuntimeError("error: vision gave an unreadable answer")
