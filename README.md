# Your Name. (2016) Canonical QA Chatbot

Live URL:
https://your-name-chatbot-bxyaynhama-uc.a.run.app

---

## Overview

This project implements a domain-specific Q&A chatbot focused strictly on the official canon of:

- *Your Name* (2016 film)
- The official light novel by Makoto Shinkai
- The official manga adaptation
- *Your Name: Another Side – Earthbound*
- Official cameo appearances of Mitsuha and Taki in *Weathering With You* (only when directly tied to Your Name continuity)

The chatbot:

- Uses a deterministic Python backstop for safety and scope control
- Uses Vertex AI (Gemini 2.0 Flash Lite) for in-domain generation
- Enforces strict canonical boundaries
- Prevents prompt injection and scope violations
- Returns structured routing decisions

---

## Architecture

### Deterministic Backstop (Python)

The system first routes every user message through a deterministic rule-based backstop:

Routes:
- `in_scope`
- `out_of_scope`
- `safety`
- `uncertain`

The backstop blocks:
- Prompt injection attempts
- Real-world religious / academic analysis
- Other anime franchises
- Fan theories / speculation
- Real-world advice
- Crisis language (safety route)

Only `in_scope` messages reach the LLM.

---

### LLM Layer

Model:
```
vertex_ai/gemini-2.0-flash-lite
```

Environment variables required:

- `VERTEX_PROJECT`
- `VERTEX_LOCATION`
- `MODEL`

The LLM is constrained by:
- Strict system prompt boundaries
- Few-shot examples
- Canon-only instructions
- Uncertainty escape hatch

---

## API Endpoints

### GET /

Serves the frontend UI.

---

### GET /healthz

Health check endpoint.

Returns:
```
{ "ok": true }
```

---

### POST /chat

Request:
```
{
  "message": "Your question"
}
```

Response:
```
{
  "answer": "...",
  "route": "in_scope | out_of_scope | safety | uncertain"
}
```

---

## Local Development

Install dependencies:

```
uv sync
```

Run locally:

```
uv run uvicorn app.main:app --reload
```

Then visit:
```
http://localhost:8000
```

---

## Deployment (Cloud Run)

Built and deployed via:

- Cloud Build
- Artifact Registry
- Cloud Run (managed)

Service account:
```
chatbot-runner@ieor-4576-agentic.iam.gserviceaccount.com
```

Public access:
```
--allow-unauthenticated
```

---

## Evaluation

Run evaluation locally:

```
uv run -m eval.run_eval
```

Evaluation data:
```
eval/data/golden.jsonl
```

---

## Design Goals

- Deterministic safety handling
- Strict canonical grounding
- Zero hallucinated cross-franchise answers
- Clear routing transparency
- Clean deployment pipeline

---

## Notes

This is not a roleplay chatbot.

It is a canon-grounded Q&A assistant with a Mitsuha-inspired narrative tone, strictly limited to official sources.

Any question outside official canon receives a deterministic out-of-scope response.