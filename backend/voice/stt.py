"""Speech-to-text with ElevenLabs: recorded audio -> the words the user said.

Owner: Michael

Docs:
  - API: https://elevenlabs.io/docs/api-reference/speech-to-text/convert
  - Python SDK (elevenlabs 2.78): https://github.com/elevenlabs/elevenlabs-python
    client.speech_to_text.convert(file=..., model_id=...)

Uses the batch model (scribe_v3): push-to-talk gives us one finished clip per request,
so we don't need the realtime/streaming API.

Try it without the mascot (records 4 s from the mic, prints what it heard):
    python -m backend.voice.stt
"""

import logging

from backend.voice.client import get_client

logger = logging.getLogger(__name__)

STT_MODEL = "scribe_v3"  # most accurate batch model

# Words Scribe might mishear: our name and common app names users will say.
KEYTERMS = ["GrizzHelper", "Chrome", "Edge", "Notepad", "File Explorer", "Word", "Outlook"]


def transcribe(wav_bytes: bytes) -> str:
    """Return the text spoken in `wav_bytes`, or "" if nothing was heard.

    On failure, log it and return "" so the mascot can say "Sorry, I didn't catch that"
    instead of crashing.
    """
    if not wav_bytes:
        return ""

    try:
        result = get_client().speech_to_text.convert(
            file=("speech.wav", wav_bytes, "audio/wav"),
            model_id=STT_MODEL,
            language_code="en",
            tag_audio_events=False,  # no "(laughs)" / "(coughs)" in the request text
            no_verbatim=True,  # drop "um", "uh" and false starts
            timestamps_granularity="none",  # we only need the text
            keyterms=KEYTERMS,
        )
    except Exception:  # noqa: BLE001 - network/auth/rate-limit: log and carry on
        logger.exception("speech-to-text failed")
        return ""

    text = (getattr(result, "text", "") or "").strip()
    logger.info("heard: %r", text)
    return text


if __name__ == "__main__":
    import sounddevice as sd

    from backend.voice.hotkey import SAMPLE_RATE, _to_wav

    logging.basicConfig(level=logging.INFO)
    seconds = 4
    print(f"Recording {seconds} s, say something...")
    # RawInputStream gives plain bytes, so no numpy needed (sd.rec() requires numpy).
    with sd.RawInputStream(samplerate=SAMPLE_RATE, channels=1, dtype="int16") as stream:
        pcm, _overflowed = stream.read(seconds * SAMPLE_RATE)

    print("You said:", transcribe(_to_wav(bytes(pcm))) or "(nothing)")
