"""Push-to-talk: hold a key to record, let go to send.

Owner: Michael

Docs:
  - keyboard 0.13.5 (global hotkeys): https://github.com/boppreh/keyboard  (on_press_key, on_release_key)
  - sounddevice 0.5.6 (microphone): https://python-sounddevice.readthedocs.io/  (RawInputStream)
  - wave (build a .wav in memory): https://docs.python.org/3/library/wave.html

Threads: keyboard callbacks run on keyboard's own thread, and the microphone callback runs
on sounddevice's audio thread. on_recording is called on the keyboard thread, so server.py
hands the clip to asyncio with asyncio.run_coroutine_threadsafe(...).

Accessibility: ONE key that's easy to hold, no chords. Users may have limited hand movement.
Holding a key fires repeated "press" events: only start recording on the first one.
"""

import io
import logging
import threading
import wave
from collections.abc import Callable

import keyboard
import sounddevice as sd

logger = logging.getLogger(__name__)

PUSH_TO_TALK_KEY = "f9"  # TODO(Michael): pick and test a key that's easy to hold
SAMPLE_RATE = 16_000  # Hz, mono: plenty for speech
SAMPLE_WIDTH = 2  # bytes per sample (int16)
MIN_SECONDS = 0.3  # ignore accidental taps shorter than this


def _to_wav(pcm: bytes) -> bytes:
    """Wrap raw 16-bit mono PCM in a WAV header, in memory."""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(SAMPLE_WIDTH)
        wav.setframerate(SAMPLE_RATE)
        wav.writeframes(pcm)
    return buf.getvalue()


class _Recorder:
    """Records from the default microphone between press and release."""

    def __init__(self, on_recording: Callable[[bytes], None]) -> None:
        self.on_recording = on_recording
        self.lock = threading.Lock()
        self.stream: sd.RawInputStream | None = None
        self.chunks: list[bytes] = []

    def _on_audio(self, indata, frames, time, status) -> None:  # noqa: ANN001 - sounddevice API
        """Audio thread: keep each block of samples as it arrives."""
        if status:
            logger.warning("mic: %s", status)
        self.chunks.append(bytes(indata))

    def on_press(self, _event: keyboard.KeyboardEvent) -> None:
        with self.lock:
            if self.stream is not None:  # key auto-repeat while held: already recording
                return
            self.chunks = []
            try:
                self.stream = sd.RawInputStream(
                    samplerate=SAMPLE_RATE, channels=1, dtype="int16", callback=self._on_audio
                )
                self.stream.start()
            except Exception:  # noqa: BLE001 - no mic, mic in use, permission denied...
                logger.exception("could not open the microphone")
                self.stream = None
                return
            logger.info("recording...")

    def on_release(self, _event: keyboard.KeyboardEvent) -> None:
        with self.lock:
            if self.stream is None:
                return
            self.stream.stop()
            self.stream.close()
            self.stream = None
            pcm = b"".join(self.chunks)
            self.chunks = []

        seconds = len(pcm) / (SAMPLE_RATE * SAMPLE_WIDTH)
        logger.info("recorded %.1f s", seconds)
        if seconds < MIN_SECONDS:
            return
        self.on_recording(_to_wav(pcm))


def start_push_to_talk(on_recording: Callable[[bytes], None]) -> None:
    """Start watching PUSH_TO_TALK_KEY and return immediately.

    While the key is held, record from the microphone. On release, call
    on_recording(wav_bytes) with the whole clip as WAV bytes.
    """
    recorder = _Recorder(on_recording)
    keyboard.on_press_key(PUSH_TO_TALK_KEY, recorder.on_press)
    keyboard.on_release_key(PUSH_TO_TALK_KEY, recorder.on_release)
    logger.info("push-to-talk ready: hold %s to speak", PUSH_TO_TALK_KEY.upper())
