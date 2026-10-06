"""Configuration, read from environment variables (see .env.example)."""
from dotenv import load_dotenv
load_dotenv()
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{ROOT / 'farashi.db'}")

# MOCK_MODE=true runs the whole pipeline WITHOUT N-ATLAS (rule-based stand-ins) so you can
# develop and test before you have GPU/model access. Set to false for the real system.
MOCK_MODE = os.getenv("MOCK_MODE", "true").lower() == "true"

# N-ATLaS LLM served through an OpenAI-compatible endpoint (e.g. vLLM).
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:8000/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "NCAIR1/N-ATLaS")
LLM_API_KEY = os.getenv("LLM_API_KEY", "none")

# N-ATLAS ASR checkpoints are language specific. Put the exact Hugging Face model ids from the
# official N-ATLAS page in your .env (ASR_MODEL_HA, ASR_MODEL_YO, ASR_MODEL_IG, ASR_MODEL_EN).
ASR_MODELS = {lang: os.getenv(f"ASR_MODEL_{lang.upper()}", "") for lang in ("ha", "yo", "ig", "en")}

# Text-to-speech: "none" = text replies only. Plug a provider into app/services/tts.py.
TTS_PROVIDER = os.getenv("TTS_PROVIDER", "none")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
PRICE_WINDOW_DAYS = int(os.getenv("PRICE_WINDOW_DAYS", "14"))

LANGUAGES = {"ha": "Hausa", "yo": "Yoruba", "ig": "Igbo", "en": "English"}
