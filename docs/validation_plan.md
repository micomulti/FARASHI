# Validation plan

**Goal:** show Farashi gives correct, useful answers to real farmers in their language.

1. **Offline accuracy:** run `data/test_questions.csv` (30-50 questions per language). Score crop extraction, intent, and answer correctness. Have a native speaker judge clarity of the reply.
2. **N-ATLAS vs generic model:** run the same local-language questions through a generic model; record where N-ATLAS does better.
3. **Pilot:** 10-20 real farmers/traders/cooperative members for 3-5 days. After each answer, collect thumbs up/down (`POST /feedback/{id}`).
4. **Report:** number of users, questions, helpful-rate, median latency, 2-3 short farmer quotes (with permission), and what you changed because of feedback.

Never invent results: report exactly what you measured, including failures.
