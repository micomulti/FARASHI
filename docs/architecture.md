# Architecture

```mermaid
flowchart LR
  F[Farmer: voice or text] --> C[Telegram / WhatsApp]
  C --> W[FastAPI webhook]
  W -->|voice| A[N-ATLAS ASR per language]
  A --> U[N-ATLaS LLM: extract crop, location, intent]
  W -->|text| U
  U --> P[(Price database)]
  P --> R[N-ATLaS LLM: phrase answer in farmer's language]
  R --> T[TTS optional]
  T --> C
  R --> C
  W --> L[(Interaction log)]
  L --> D[Streamlit dashboard]
```

Two-call pattern: the LLM (1) turns a free-form question into a small JSON form, then (2) phrases an answer from
database rows it is given. This is more reliable on an 8B model than open-ended tool calling, and guarantees every
price shown comes from the database.
