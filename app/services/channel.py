"""Telegram helpers (fastest channel for a demo). For WhatsApp, add the same two functions
for Twilio or Meta Cloud API and call them from the webhook in main.py."""
import httpx

from app.config import TELEGRAM_TOKEN

API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
FILE_API = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}"


def send_text(chat_id: int, text: str) -> None:
    httpx.post(f"{API}/sendMessage", json={"chat_id": chat_id, "text": text}, timeout=20)


def send_voice(chat_id: int, audio: bytes) -> None:
    httpx.post(f"{API}/sendVoice", data={"chat_id": chat_id}, files={"voice": ("reply.ogg", audio)}, timeout=30)


def download_voice(file_id: str, dest: str) -> str:
    info = httpx.get(f"{API}/getFile", params={"file_id": file_id}, timeout=20).json()["result"]
    with open(dest, "wb") as f:
        f.write(httpx.get(f"{FILE_API}/{info['file_path']}", timeout=30).content)
    return dest
