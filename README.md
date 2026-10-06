# Farashi

**A voice-first AI assistant, built on N-ATLAS, that tells Nigerian smallholder farmers current crop prices and where to sell, in their own language.**

Built for the National AI Innovation Challenge (NAIC), Innovation & Enterprise Track.

## What it does
A farmer sends a voice note or message (Hausa, Yoruba, Igbo or English), e.g. *"Ina zan sayar da tumatir na?"*.
Farashi understands the question, looks up recent prices from its own database, and replies with the best markets and prices.

```
Farmer (Telegram / WhatsApp voice or text)
   -> FastAPI webhook
   -> ASR (N-ATLAS, per language)            voice -> text
   -> N-ATLaS LLM: extract {crop, location, intent}
   -> Price service (database)               prices come from DATA, never from the model
   -> N-ATLaS LLM: phrase a short answer in the farmer's language
   -> TTS (optional) -> reply as text (+ voice)
   -> Log to DB -> Streamlit dashboard
```

Design rule: **the model never invents prices.** It only understands the question and phrases the answer;
every number comes from the `prices` table.

## Status: read this first
| Part | State |
|---|---|
| FastAPI app, database, price logic, pipeline, feedback, dashboard | Built and tested (9 tests) |
| Telegram webhook | Written, **not yet tested against live Telegram** |
| N-ATLaS LLM calls | Written for an OpenAI-compatible endpoint (e.g. vLLM); **needs your model access** |
| N-ATLAS ASR | Wrapper written; **you must set the checkpoint ids** in `.env` |
| Text-to-speech | **Not included**; stub returns text-only replies |
| Price data | `data/prices_seed.csv` contains **PLACEHOLDER numbers**. Replace with real survey data |

`MOCK_MODE=true` (default) swaps the LLM for rule-based stand-ins so everything can be developed and tested without a GPU.
In mock mode replies are English-only. **Do not present mock-mode output as N-ATLAS output** in your submission.

## Quick start (mock mode, no GPU)
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m app.db.seed data/prices_seed.csv
uvicorn app.main:app --reload            # http://127.0.0.1:8000/docs
pytest
streamlit run dashboard/app.py           # usage dashboard
```
Try it:
```bash
curl -X POST localhost:8000/ask -H "Content-Type: application/json" \
  -d '{"phone":"2348000000001","text":"Ina zan sayar da tumatir na?","language":"ha"}'
```

## Going live with N-ATLAS
1. Get the model: `NCAIR1/N-ATLaS` on Hugging Face (check the official page for current terms and access).
2. Serve it on a GPU machine, e.g. `vllm serve NCAIR1/N-ATLaS --max-model-len 8192 --port 8000`.
3. In `.env`: `MOCK_MODE=false`, set `LLM_BASE_URL`, and the `ASR_MODEL_*` ids from the official N-ATLAS page.
4. `pip install transformers torch` for ASR, then test voice with `POST /ask-voice`.
5. Telegram: create a bot with @BotFather, set `TELEGRAM_TOKEN`, then point the webhook at `https://<your-host>/webhook/telegram`.
6. Capture screenshots/logs of real N-ATLAS calls: this is your **integration evidence**.

## Project structure
```
app/
  main.py            FastAPI routes: /ask, /ask-voice, /feedback, /webhook/telegram, /health
  pipeline.py        orchestrates the whole flow
  config.py          environment configuration
  services/          llm.py  asr.py  tts.py  prices.py  channel.py
  db/                models.py  seed.py
  prompts/           extract.txt  answer.txt
admin/update_prices.py   field-agent price entry
dashboard/app.py         Streamlit usage + feedback dashboard
data/                    prices_seed.csv (placeholder), test_questions.csv
tests/                   pytest suite
docs/                    build plan, validation plan, submission checklist
```

## Adding a language or crop
- **Crop:** add it with local-name aliases in `app/db/seed.py` (`CROP_ALIASES`; lowercase, no accents). Have native speakers verify spellings.
- **Language:** add its code to `LANGUAGES` in `config.py`, set `ASR_MODEL_<CODE>`, and add test questions.

## Known limitations
- Prices are only as good as the survey data behind them; every answer states the data date.
- Crop matching is alias-based; new spellings need adding.
- N-ATLaS has a short (~8k token) context window, so prompts send only the top price rows.
- Pidgin: confirm official N-ATLAS support before promising it.
- N-ATLAS licence terms (attribution, user caps) should be checked before scaling beyond a pilot.

## Privacy
Phone numbers are stored only as SHA-256 hashes. Show a consent message on first contact in your channel flow.
