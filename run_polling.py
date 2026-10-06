"""Local Telegram runner (polling): python run_polling.py"""
import tempfile
import time

import httpx

from app import pipeline
from app.config import TELEGRAM_TOKEN
from app.db.models import SessionLocal, init_db
from app.services import channel

API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
WELCOME = ("Welcome to Farashi. Ask me the price of a crop or where to sell it, "
           "for example: Where should I sell my tomatoes?")


def main():
    if not TELEGRAM_TOKEN:
        raise SystemExit("Set TELEGRAM_TOKEN in .env first")
    init_db()
    httpx.get(f"{API}/deleteWebhook", timeout=20)  # polling and webhooks cannot run together
    offset = None
    print("Farashi bot is running. Press Ctrl+C to stop.")
    while True:
        try:
            params = {"timeout": 30}
            if offset:
                params["offset"] = offset
            updates = httpx.get(f"{API}/getUpdates", params=params, timeout=40).json().get("result", [])
            for upd in updates:
                offset = upd["update_id"] + 1
                msg = upd.get("message")
                if not msg:
                    continue
                chat_id = msg["chat"]["id"]
                if msg.get("text", "").startswith("/start"):
                    channel.send_text(chat_id, WELCOME)
                    continue
                with SessionLocal() as db:
                    user = pipeline.get_or_create_user(db, str(chat_id))
                    try:
                        if "voice" in msg:
                            path = channel.download_voice(msg["voice"]["file_id"], tempfile.mktemp(suffix=".ogg"))
                            out = pipeline.handle(db, user, audio_path=path)
                        elif "text" in msg:
                            out = pipeline.handle(db, user, text=msg["text"])
                        else:
                            continue
                        channel.send_text(chat_id, out["answer"])
                    except Exception as e:
                        print("Error:", e)
                        channel.send_text(chat_id, "Sorry, something went wrong. Please try again.")
        except httpx.HTTPError as e:
            print("Network error, retrying:", e)
            time.sleep(3)
        except KeyboardInterrupt:
            print("Stopped.")
            break


if __name__ == "__main__":
    main()