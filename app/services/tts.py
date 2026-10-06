"""Text-to-speech. Returns audio bytes, or None to send a text-only reply.

No TTS provider is wired in by default. Test candidate tools for your language EARLY; if none sounds
acceptable, keep voice input + clear text output and say so honestly in your submission.
"""
from app.config import TTS_PROVIDER


def speak(text: str, language: str) -> bytes | None:
    if TTS_PROVIDER == "none":
        return None
    raise NotImplementedError(f"Implement TTS provider '{TTS_PROVIDER}' here.")
