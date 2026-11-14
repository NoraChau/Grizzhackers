"""Text-to-speech with ElevenLabs: read the agent's reply out loud.

Owner: Experienced #2
Docs: https://elevenlabs.io/docs/api-reference/text-to-speech/convert
"""


def speak(text: str) -> None:
    """Say `text` out loud using the voice in ELEVENLABS_VOICE_ID. Blocks until playback ends.

    TODO(exp2):
    - Tip: request a raw PCM output_format (the docs list pcm_16000, pcm_22050, ...).
      Raw PCM can be played directly with sounddevice; MP3 would need an extra decoder.
    - Also show the reply in the overlay transcript, for users who can't hear it.
    """
    raise NotImplementedError("TODO(exp2): speak")
