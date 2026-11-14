"""Speech-to-text with ElevenLabs.

Owner: Michael
Docs: https://elevenlabs.io/docs/api-reference/speech-to-text/convert
"""


def transcribe(audio_wav: bytes) -> str:
    """Send recorded audio to ElevenLabs and return what the user said, as text.

    Return "" for silence or noise so the agent isn't called with nothing.
    TODO(exp2): read ELEVENLABS_API_KEY from the environment; never print it.
    """
    raise NotImplementedError("TODO(exp2): transcribe")
