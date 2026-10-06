"""Load crops and prices from CSV.   python -m app.db.seed data/prices_seed.csv

IMPORTANT: data/prices_seed.csv ships with PLACEHOLDER numbers so the system runs.
Replace them with real, dated prices from your market survey before any demo or pilot.
"""
import csv
import sys
from datetime import date

from app.db.models import Crop, Market, Price, SessionLocal, init_db

# Local-name aliases (lowercase, no accents). Have native speakers verify and extend these.
CROP_ALIASES = {
    "tomato": "tumatir,tomati,tomato",
    "maize": "masara,agbado,oka,maize,corn",
    "rice": "shinkafa,iresi,osikapa,rice",
    "beans": "wake,ewa,agwa,beans",
    "yam": "doya,isu,ji,yam",
    "onion": "albasa,alubosa,yabasi,onion",
    "pepper": "barkono,ata,pepper",
}


def seed(csv_path: str) -> int:
    init_db()
    n = 0
    with SessionLocal() as db:
        for name, aliases in CROP_ALIASES.items():
            if not db.query(Crop).filter_by(name_en=name).first():
                db.add(Crop(name_en=name, aliases=aliases))
        db.commit()
        with open(csv_path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                crop = db.query(Crop).filter_by(name_en=row["crop"].strip().lower()).first()
                if not crop:
                    continue
                market = db.query(Market).filter_by(name=row["market"].strip()).first()
                if not market:
                    market = Market(name=row["market"].strip(), state=row["state"].strip())
                    db.add(market)
                    db.flush()
                d = date.fromisoformat(row["date"]) if row.get("date") else date.today()
                db.add(Price(crop_id=crop.id, market_id=market.id, price=float(row["price"]),
                             unit=row["unit"].strip(), date=d, source=row.get("source", "field survey")))
                n += 1
        db.commit()
    return n


if __name__ == "__main__":
    print(f"Seeded {seed(sys.argv[1] if len(sys.argv) > 1 else 'data/prices_seed.csv')} price rows")
