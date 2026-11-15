"""Text-to-speech with ElevenLabs: say GrizzHelper's reply out loud.

Owner: Michael

Docs:
  - API: https://elevenlabs.io/docs/api-reference/text-to-speech/stream
  - Python SDK (elevenlabs 2.78): https://github.com/elevenlabs/elevenlabs-python
    client.text_to_speech.stream(voice_id=..., text=..., model_id=..., output_format=...)
Voice id comes from ELEVENLABS_VOICE_ID in .env.

How it plays: we ask for raw PCM (16-bit mono samples, no file header) and write the
chunks straight into a sounddevice output stream AS THEY ARRIVE, so the bear starts
talking before the whole clip has downloaded. No ffmpeg, no numpy.

Try it without the mascot (uses a few credits):
    python -m backend.voice.tts "Hi, I'm GrizzHelper."
"""

import logging
import os

import sounddevice as sd
from elevenlabs.core.api_error import ApiError

from backend.voice.client import get_client

logger = logging.getLogger(__name__)

# Flash = lowest latency (~75 ms), which matters more than max quality for short replies.
TTS_MODEL = "eleven_flash_v2_5"
SAMPLE_RATE = 24_000  # must match OUTPUT_FORMAT
OUTPUT_FORMAT = f"pcm_{SAMPLE_RATE}"  # raw signed 16-bit little-endian mono
FRAME_BYTES = 2  # one int16 sample per frame (mono)


def speak(text: str) -> None:
    """Say `text` out loud and return when it has finished playing.

    Replies should already be short (1-2 sentences): long text = long waits + more credits.
    On failure, log it and return: the reply is still visible in the bubble.
    """
    text = text.strip()
    if not text:
        return
    voice_id = os.getenv("ELEVENLABS_VOICE_ID")
    if not voice_id:
        logger.error("ELEVENLABS_VOICE_ID is not set in .env; not speaking")
        return

    try:
        audio_chunks = get_client().text_to_speech.stream(
            voice_id=voice_id,
            text=text,
            model_id=TTS_MODEL,
            output_format=OUTPUT_FORMAT,
        )
        with sd.RawOutputStream(samplerate=SAMPLE_RATE, channels=1, dtype="int16") as out:
            leftover = b""
            for chunk in audio_chunks:
                # Network chunks can split a 2-byte sample in half: only play whole samples.
                data = leftover + chunk
                cut = len(data) - len(data) % FRAME_BYTES
                if cut:
                    out.write(data[:cut])  # blocks until the device takes it
                leftover = data[cut:]
        # Leaving the `with` block waits for the buffered audio to finish playing.
    except ApiError as e:  # e.g. 402: free plans can't use library voices, pick a premade one
        detail = e.body.get("detail") if isinstance(e.body, dict) else None
        message = detail.get("message") if isinstance(detail, dict) else detail
        logger.error("text-to-speech failed (HTTP %s): %s", e.status_code, message or e.body)
    except Exception:  # noqa: BLE001 - network/auth/no speakers: the bubble still shows it
        logger.exception("text-to-speech failed")


if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO)
    speak(" ".join(sys.argv[1:]) or "Hi, I'm GrizzHelper. How can I help?")
