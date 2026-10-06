# Farashi build plan (9 days to the 12 October 2026 deadline)

| Day | Goal | Done when |
|---|---|---|
| 1 | Repo + roles; confirm how you will run N-ATLAS; pick ONE language and 3-5 crops | Model answers one test sentence |
| 1-2 | Collect REAL prices from 3-5 markets (visits/phone calls) | `prices_seed.csv` has real, dated rows |
| 2-3 | Serve the LLM; set ASR checkpoint for your language | `/ask` works with MOCK_MODE=false |
| 3-5 | Tune prompts; extend crop aliases; run `data/test_questions.csv` | >= 85% crop+intent accuracy |
| 4-5 | Telegram (or WhatsApp) channel live | A phone can ask and get an answer |
| 5-6 | Test TTS options in your language | Decision: voice-out or text-out |
| 6-8 | Pilot with 10-20 real farmers/traders; collect thumbs up/down; compare vs a generic model | Dashboard shows real usage |
| 8-9 | README, architecture diagram, integration screenshots, 3-5 min demo video, team profiles, ID docs | Submitted a day early |

## Roles (4 people)
1. Backend + N-ATLAS integration
2. Data + testing (prices, test questions, scoring)
3. Channel + voice (Telegram/WhatsApp, ASR, TTS)
4. Docs + pitch (README, video, business case, form answers)

## Fallbacks
- No GPU: quantised model on Colab/Kaggle, or ask about compute credits at onboarding clinics.
- ASR weak on accents/noise: ask the farmer to repeat; allow text.
- No good TTS: voice in, text out. State it honestly.
- Not enough real prices: fewer crops and markets, but all real and dated.
