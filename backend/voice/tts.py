"""Text-to-speech with ElevenLabs: say GrizzHelper's reply out loud.

Owner: Michael

Docs:
  - API: https://elevenlabs.io/docs/api-reference/text-to-speech/convert
  - Python SDK (elevenlabs 2.78): https://github.com/elevenlabs/elevenlabs-python
    client.text_to_speech.convert(voice_id=..., text=..., model_id=..., output_format=...)
Voice id comes from ELEVENLABS_VOICE_ID.

Windows gotcha: the SDK's play() helper uses ffmpeg by default, which most laptops don't
have. Easier: ask for a raw PCM output_format (e.g. "pcm_22050") and play it with
sounddevice (sd.play(...) then sd.wait()).
"""


def speak(text: str) -> None:
    """Say `text` out loud and return when it has finished playing.

    Replies should already be short (1-2 sentences): long text = long waits + more credits.
    On failure, log it and return: the reply is still visible in the bubble.

    TODO(Michael): implement.
    """
    raise NotImplementedError("TODO(Michael): speak")
