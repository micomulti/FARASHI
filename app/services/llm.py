"""N-ATLaS LLM client (OpenAI-compatible endpoint) with a rule-based MOCK mode for offline development."""
import json
import re
from pathlib import Path

from app.config import LANGUAGES, LLM_API_KEY, LLM_BASE_URL, LLM_MODEL, MOCK_MODE

PROMPTS = Path(__file__).resolve().parent.parent / "prompts"
_client = None


def _chat(system: str, user: str, temperature: float = 0.0, max_tokens: int = 200) -> str:
    global _client
    if _client is None:
        from openai import OpenAI
        _client = OpenAI(base_url=LLM_BASE_URL, api_key=LLM_API_KEY)
    resp = _client.chat.completions.create(
        model=LLM_MODEL, temperature=temperature, max_tokens=max_tokens,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}])
    return resp.choices[0].message.content.strip()


def extract(question: str) -> dict:
    """Turn a farmer's question into {crop, location, intent}."""
    if MOCK_MODE:
        return {"crop": None, "location": None, "intent": "best_market"}  # crop is resolved from text by prices.py
    raw = _chat((PROMPTS / "extract.txt").read_text(), question)
    match = re.search(r"\{.*\}", raw, re.S)
    try:
        data = json.loads(match.group(0)) if match else {}
    except json.JSONDecodeError:
        data = {}
    if data.get("intent") not in {"best_market", "price", "unclear"}:
        data["intent"] = "unclear"
    return data


def phrase_answer(rows: list[dict], language: str) -> str:
    """Write the farmer-facing reply from DATABASE rows only."""
    if MOCK_MODE:
        if not rows:
            return "I have no recent price for that crop yet. Please check again soon."
        top = rows[0]
        extras = "; ".join(f"{r['market']} {r['avg_price']}" for r in rows[1:])
        return (f"Best price: {top['market']} ({top['state']}) at about {top['avg_price']} per {top['unit']} "
                f"(data to {top['latest']})." + (f" Also: {extras}." if extras else ""))
    system = (PROMPTS / "answer.txt").read_text().format(
        language=LANGUAGES.get(language, "English"), data=json.dumps(rows, ensure_ascii=False))
    return _chat(system, "Answer the farmer now.", temperature=0.2, max_tokens=160)


def ask_to_repeat(language: str) -> str:
    if MOCK_MODE:
        return "Sorry, I did not understand. Please say the crop name again, for example: tomato or maize."
    return _chat(f"Reply in {LANGUAGES.get(language, 'English')}, one short sentence. "
                 "Politely ask the farmer to repeat which crop they want the price of.", "Please repeat.", 0.2, 60)
