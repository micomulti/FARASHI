"""Speech-to-text with N-ATLAS language-specific ASR models.

Set ASR_MODEL_HA / _YO / _IG / _EN in .env to the exact checkpoint ids from the official N-ATLAS page.
"""
from app.config import ASR_MODELS, MOCK_MODE

_pipes: dict = {}


def transcribe(audio_path: str, language: str) -> str:
    if MOCK_MODE:
        raise RuntimeError("Voice input needs MOCK_MODE=false and an ASR model. Use text in mock mode.")
    model_id = ASR_MODELS.get(language)
    if not model_id:
        raise RuntimeError(f"No ASR model configured for '{language}'. Set ASR_MODEL_{language.upper()}.")
    if language not in _pipes:
        from transformers import pipeline  # imported lazily: heavy dependency
        _pipes[language] = pipeline("automatic-speech-recognition", model=model_id)
    return _pipes[language](audio_path)["text"].strip()
