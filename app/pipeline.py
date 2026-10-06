"""Orchestrates: (ASR) -> understand -> price lookup -> phrase -> (TTS) -> log."""
import hashlib
import json
import time

from sqlalchemy.orm import Session

from app.db.models import Interaction, User
from app.services import asr, llm, prices, tts


def get_or_create_user(db: Session, phone: str, language: str = "ha") -> User:
    h = hashlib.sha256(phone.encode()).hexdigest()  # never store raw phone numbers
    user = db.query(User).filter_by(phone_hash=h).first()
    if not user:
        user = User(phone_hash=h, language=language)
        db.add(user)
        db.commit()
    return user


def handle(db: Session, user: User, text: str | None = None, audio_path: str | None = None) -> dict:
    start = time.time()
    input_type = "voice" if audio_path else "text"
    transcript = text if text else asr.transcribe(audio_path, user.language)

    intent = llm.extract(transcript)
    crop = prices.resolve_crop(db, intent.get("crop") or transcript)
    intent["crop_resolved"] = crop.name_en if crop else None

    if crop is None or intent.get("intent") == "unclear":
        answer = llm.ask_to_repeat(user.language)
        rows = []
    else:
        rows = prices.best_markets(db, crop.id, intent.get("location") or user.state or None)
        answer = llm.phrase_answer(rows, user.language)

    audio = tts.speak(answer, user.language)
    latency = int((time.time() - start) * 1000)
    rec = Interaction(user_id=user.id, input_type=input_type, transcript=transcript,
                      intent_json=json.dumps(intent, ensure_ascii=False), answer=answer, latency_ms=latency)
    db.add(rec)
    db.commit()
    return {"interaction_id": rec.id, "transcript": transcript, "intent": intent,
            "answer": answer, "audio": audio, "latency_ms": latency}
