"""Push-to-talk: hold a key to record, let go to send.

Owner: Michael

Docs:
  - keyboard 0.13.5 (global hotkeys): https://github.com/boppreh/keyboard  (on_press_key, on_release_key)
  - sounddevice 0.5.6 (microphone): https://python-sounddevice.readthedocs.io/  (InputStream)
  - wave (build a .wav in memory): https://docs.python.org/3/library/wave.html

Threads gotcha: keyboard callbacks run on keyboard's own thread, not the asyncio loop.
To hand the audio to server.py, use loop.call_soon_threadsafe(...) or
asyncio.run_coroutine_threadsafe(...).

Accessibility: ONE key that's easy to hold, no chords. Users may have limited hand movement.
Holding a key fires repeated "press" events: only start recording on the first one.
"""

from collections.abc import Callable

PUSH_TO_TALK_KEY = "f9"  # TODO(Michael): pick and test a key that's easy to hold
SAMPLE_RATE = 16_000  # Hz, mono: plenty for speech


def start_push_to_talk(on_recording: Callable[[bytes], None]) -> None:
    """Start watching PUSH_TO_TALK_KEY and return immediately.

    While the key is held, record from the microphone. On release, call
    on_recording(wav_bytes) with the whole clip as WAV bytes.

    TODO(Michael): implement.
    """
    raise NotImplementedError("TODO(Michael): start_push_to_talk")
