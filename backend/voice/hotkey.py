"""Microphone recording, started by holding a key (push-to-talk) or the mascot's mic button.

Owner: Michael

Two ways to record, both using the same Recorder:
  - Hold PUSH_TO_TALK_KEY: press starts, release stops.
  - Mic button in the mascot: one click starts, the next click stops (server.py calls
    recorder.start() / recorder.stop()).
When a recording stops, the clip goes to on_recording(wav_bytes).

Docs:
  - keyboard 0.13.5 (global hotkeys): https://github.com/boppreh/keyboard  (on_press_key, on_release_key)
  - sounddevice 0.5.6 (microphone): https://python-sounddevice.readthedocs.io/  (RawInputStream)
  - wave (build a .wav in memory): https://docs.python.org/3/library/wave.html

Threads: start()/stop() get called from the keyboard thread (hotkey), the asyncio loop
(button) and a timer thread (MAX_SECONDS), so a lock guards the state. Callbacks run on
whichever thread triggered them: server.py hands them to asyncio thread-safely.

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
MAX_SECONDS = 30  # a mic left on by the button stops itself after this long


def _to_wav(pcm: bytes) -> bytes:
    """Wrap raw 16-bit mono PCM in a WAV header, in memory."""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(SAMPLE_WIDTH)
        wav.setframerate(SAMPLE_RATE)
        wav.writeframes(pcm)
    return buf.getvalue()


class Recorder:
    """Records from the default microphone between start() and stop()."""

    def __init__(
        self,
        on_recording: Callable[[bytes], None],
        on_status: Callable[[bool], None] | None = None,
    ) -> None:
        self.on_recording = on_recording  # gets the finished clip as WAV bytes
        self.on_status = on_status  # gets True when recording starts, False when it stops
        self.lock = threading.Lock()
        self.stream: sd.RawInputStream | None = None
        self.chunks: list[bytes] = []
        self.timer: threading.Timer | None = None

    @property
    def recording(self) -> bool:
        return self.stream is not None

    def _on_audio(self, indata, frames, time, status) -> None:  # noqa: ANN001 - sounddevice API
        """Audio thread: keep each block of samples as it arrives."""
        if status:
            logger.warning("mic: %s", status)
        self.chunks.append(bytes(indata))

    def start(self) -> None:
        """Open the mic and start recording. Does nothing if already recording."""
        with self.lock:
            if self.stream is not None:  # key auto-repeat, or button + key: already recording
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
            self.timer = threading.Timer(MAX_SECONDS, self.stop)
            self.timer.daemon = True
            self.timer.start()
        logger.info("recording...")
        if self.on_status:
            self.on_status(True)

    def stop(self) -> None:
        """Stop recording and hand the clip to on_recording. Does nothing if not recording."""
        with self.lock:
            if self.stream is None:
                return
            self.stream.stop()
            self.stream.close()
            self.stream = None
            if self.timer is not None:
                self.timer.cancel()
                self.timer = None
            pcm = b"".join(self.chunks)
            self.chunks = []

        if self.on_status:
            self.on_status(False)
        seconds = len(pcm) / (SAMPLE_RATE * SAMPLE_WIDTH)
        logger.info("recorded %.1f s", seconds)
        if seconds < MIN_SECONDS:
            return
        self.on_recording(_to_wav(pcm))


def start_push_to_talk(
    on_recording: Callable[[bytes], None],
    on_status: Callable[[bool], None] | None = None,
) -> Recorder:
    """Start watching PUSH_TO_TALK_KEY and return immediately.

    While the key is held, record from the microphone. On release, call
    on_recording(wav_bytes) with the whole clip as WAV bytes. Returns the Recorder so the
    mic button can use it too.
    """
    recorder = Recorder(on_recording, on_status)
    keyboard.on_press_key(PUSH_TO_TALK_KEY, lambda _event: recorder.start())
    keyboard.on_release_key(PUSH_TO_TALK_KEY, lambda _event: recorder.stop())
    logger.info("push-to-talk ready: hold %s to speak", PUSH_TO_TALK_KEY.upper())
    return recorder
