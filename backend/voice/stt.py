"""Speech-to-text with ElevenLabs: recorded audio -> the words the user said.

Owner: Michael

Docs:
  - API: https://elevenlabs.io/docs/api-reference/speech-to-text/convert
  - Python SDK (elevenlabs 2.78): https://github.com/elevenlabs/elevenlabs-python
    client.speech_to_text.convert(file=..., model_id=...)
Check the docs for the current speech-to-text model_id; don't guess.
Use ONE shared ElevenLabs(api_key=...) client for stt.py and tts.py.
"""


def transcribe(wav_bytes: bytes) -> str:
    """Return the text spoken in `wav_bytes`, or "" if nothing was heard.

    On failure, log it and return "" so the mascot can say "Sorry, I didn't catch that"
    instead of crashing.

    TODO(Michael): implement.
    """
    raise NotImplementedError("TODO(Michael): transcribe")
