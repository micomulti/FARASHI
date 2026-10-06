"""Crop resolution and best-market logic. Prices ALWAYS come from the database, never from the LLM."""
import unicodedata
from datetime import date, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.config import PRICE_WINDOW_DAYS
from app.db.models import Crop, Market, Price


def normalize(text: str) -> str:
    """Lowercase and strip accents so 'tòmátì' matches 'tomati'."""
    text = unicodedata.normalize("NFKD", text.lower())
    return "".join(c for c in text if not unicodedata.combining(c)).strip()


def resolve_crop(db: Session, text: str) -> Crop | None:
    """Find a crop whose English name or local alias appears in `text`."""
    t = normalize(text)
    for crop in db.query(Crop).all():
        names = [normalize(crop.name_en)] + [normalize(a) for a in crop.aliases.split(",") if a]
        if any(n and n in t for n in names):
            return crop
    return None


def best_markets(db: Session, crop_id: int, state: str | None = None, top: int = 3) -> list[dict]:
    """Average recent price per market, highest first (best place for a farmer to SELL)."""
    since = date.today() - timedelta(days=PRICE_WINDOW_DAYS)
    q = (db.query(Market.name, Market.state, func.avg(Price.price), func.max(Price.date), Price.unit)
         .join(Price, Price.market_id == Market.id)
         .filter(Price.crop_id == crop_id, Price.date >= since))
    if state:
        q = q.filter(func.lower(Market.state) == state.lower())
    rows = q.group_by(Market.name, Market.state, Price.unit).order_by(func.avg(Price.price).desc()).limit(top).all()
    return [{"market": r[0], "state": r[1], "avg_price": round(r[2]), "latest": r[3].isoformat(), "unit": r[4]}
            for r in rows]
