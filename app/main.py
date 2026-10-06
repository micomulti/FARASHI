"""FastAPI app.   uvicorn app.main:app --reload"""
import tempfile

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from app import pipeline
from app.config import LANGUAGES, MOCK_MODE, TELEGRAM_TOKEN
from app.db.models import Interaction, SessionLocal, init_db
from app.services import channel

app = FastAPI(title="Farashi", description="Voice-first market price assistant for Nigerian farmers")
init_db()

@app.get("/")
def home():
    return {"name": "Farashi", "docs": "/docs", "health": "/health"}

def get_db():
    with SessionLocal() as db:
        yield db


class AskIn(BaseModel):
    phone: str
    text: str
    language: str = "ha"


@app.get("/health")
def health():
    return {"status": "ok", "mock_mode": MOCK_MODE, "languages": LANGUAGES}


@app.post("/ask")
def ask(body: AskIn, db=Depends(get_db)):
    """Text endpoint, handy for testing and the demo."""
    if body.language not in LANGUAGES:
        raise HTTPException(400, f"language must be one of {list(LANGUAGES)}")
    user = pipeline.get_or_create_user(db, body.phone, body.language)
    out = pipeline.handle(db, user, text=body.text)
    out.pop("audio", None)
    return out


@app.post("/ask-voice")
async def ask_voice(phone: str = Form(...), language: str = Form("ha"), audio: UploadFile = File(...), db=Depends(get_db)):
    with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as f:
        f.write(await audio.read())
    user = pipeline.get_or_create_user(db, phone, language)
    out = pipeline.handle(db, user, audio_path=f.name)
    out.pop("audio", None)
    return out


@app.post("/feedback/{interaction_id}")
def feedback(interaction_id: int, helpful: bool, db=Depends(get_db)):
    rec = db.get(Interaction, interaction_id)
    if not rec:
        raise HTTPException(404, "interaction not found")
    rec.rating = 1 if helpful else 0
    db.commit()
    return {"ok": True}


@app.post("/webhook/telegram")
async def telegram_webhook(update: dict, db=Depends(get_db)):
    msg = update.get("message")
    if not msg or not TELEGRAM_TOKEN:
        return {"ok": True}
    chat_id = msg["chat"]["id"]
    user = pipeline.get_or_create_user(db, str(chat_id))
    if "voice" in msg:
        path = channel.download_voice(msg["voice"]["file_id"], tempfile.mktemp(suffix=".ogg"))
        out = pipeline.handle(db, user, audio_path=path)
    elif "text" in msg:
        out = pipeline.handle(db, user, text=msg["text"])
    else:
        return {"ok": True}
    channel.send_text(chat_id, out["answer"])
    if out.get("audio"):
        channel.send_voice(chat_id, out["audio"])
    return {"ok": True}
