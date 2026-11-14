"""Push-to-talk: hold a key to record the microphone, release it to stop.

Owner: Michael
Docs:
    Global hotkeys (keyboard): https://github.com/boppreh/keyboard
    Microphone (sounddevice):  https://python-sounddevice.readthedocs.io/
"""

from collections.abc import Callable

# TODO(exp2): pick the key. A single key is easier than a chord for people with RSI.
PUSH_TO_TALK_KEY = "f8"
SAMPLE_RATE = 16_000  # 16 kHz mono is plenty for speech


def start_listening(on_audio: Callable[[bytes], None]) -> None:
    """Start listening in the background: record while the key is held, then call on_audio(wav_bytes).

    TODO(exp2):
    - Holding a key fires many "down" events (auto-repeat). Start recording only on the first one.
    - The stdlib `wave` module can wrap raw 16-bit samples into WAV bytes.
    - on_audio runs on the keyboard library's thread, not the asyncio loop. To call async code
      from there, use asyncio.run_coroutine_threadsafe(coro, loop).
    - Send "status": "listening" while recording so the orb reacts.
    """
    raise NotImplementedError("TODO(exp2): start_listening")
