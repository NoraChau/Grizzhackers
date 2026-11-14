"""Tools: screenshot + Gemini vision. Answers "What's on my screen?" (hero task 2).

Vision is the last resort for acting (slow, can be wrong). Prefer ui.py for clicking.

Owner: Intermediate
Docs:
    Screenshots (mss):  https://python-mss.readthedocs.io/
    Gemini vision:      https://ai.google.dev/gemini-api/docs/image-understanding
    Gemini models:      https://ai.google.dev/gemini-api/docs/models
Privacy: screenshots can contain private info. Send them to Gemini only; don't save them to Atlas or disk.
"""


def take_screenshot() -> bytes:
    """Capture the primary monitor and return PNG bytes.

    TODO(intermediate)
    """
    raise NotImplementedError("TODO(intermediate): take_screenshot")


def describe_screen(question: str = "What's on my screen?") -> str:
    """Take a screenshot and ask Gemini `question` about it. Return a short, speakable answer.

    TODO(intermediate): read GEMINI_API_KEY from the environment; never print it.
    """
    raise NotImplementedError("TODO(intermediate): describe_screen")
