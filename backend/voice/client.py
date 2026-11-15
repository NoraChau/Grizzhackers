"""The one shared ElevenLabs client for stt.py and tts.py.

Owner: Michael

The key comes from ELEVENLABS_API_KEY in the environment. Never put the key in code:
it lives in .env (gitignored), which load_dotenv() loads.
"""

import os
from functools import cache

from dotenv import load_dotenv

# override=True: a terminal opened before the key was added can hold an EMPTY
# ELEVENLABS_API_KEY, and plain load_dotenv() never replaces an existing variable.
load_dotenv(override=True)

from elevenlabs import ElevenLabs  # after load_dotenv, see get_client


@cache
def get_client() -> ElevenLabs:
    """Create the client on first use, then reuse it.

    Pass the key explicitly: ElevenLabs() defaults to os.getenv("ELEVENLABS_API_KEY")
    evaluated when the elevenlabs package is IMPORTED, so if anything imports it before
    .env is loaded, the client silently gets no key (401 "Neither authorization header
    nor xi-api-key received").
    """
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        raise RuntimeError("ELEVENLABS_API_KEY is not set: add it to .env")
    return ElevenLabs(api_key=api_key)
