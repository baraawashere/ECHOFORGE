# ECHOFORGE — Cognitive Memory Engine for Student Mistakes

Built for the USAII Global AI Hackathon 2026.

Every tutoring tool today treats mistakes as isolated events: get a question
wrong, get corrected, move on. None of them ask whether a mistake made this
week is secretly the same misunderstanding as a mistake made two weeks ago
in a completely different subject.

ECHOFORGE does. It remembers every mistake a student has ever made, searches
across that history for mistakes that share a root cause even across
subjects, and asks an LLM to explain that root cause in plain language —
live, on a dashboard.

## Architecture

```
echoforge/
├── backend/                       FastAPI
│   ├── app/
│   │   ├── config.py              Settings, loaded from .env
│   │   ├── models.py              Pydantic schemas (Answer, GapCluster, etc.)
│   │   ├── curriculum_standards.py  Real Common Core standards, not free text
│   │   ├── embedding_service.py   Sentence-Transformers wrapper
│   │   ├── memory_store.py        ChromaDB wrapper — the memory layer
│   │   ├── root_cause_engine.py   Calls Claude to find shared root causes
│   │   ├── websocket_manager.py   Streams live analysis to the frontend
│   │   ├── cluster_store.py       Persists discovered connections to disk
│   │   └── main.py                FastAPI app — all REST + WS routes
│   ├── scripts/
│   │   └── seed_demo_data.py      Builds a synthetic student history for the demo
│   └── requirements.txt
└── frontend/                      React + Vite
    └── src/
        ├── App.jsx
        ├── api.js
        ├── useAnalysisSocket.js   WebSocket hook with auto-reconnect
        └── components/
            ├── CognitiveGapMap.jsx   The dashboard: a timeline of mistakes,
            │                        with arcs connecting shared root causes
            ├── AnswerSubmitForm.jsx
            └── LiveAnalysisFeed.jsx
```

## How it works

1. A student submits an answer → `POST /api/answers`
2. The answer is embedded (Sentence-Transformers) and stored in ChromaDB,
   tagged with the real Common Core standard it falls under
3. If the answer is wrong, the backend searches that same student's other
   wrong answers for ones that are semantically close, even across subjects
4. If related mistakes are found, they're sent to Claude (`claude-sonnet-4-6`),
   which is asked to identify the one misconception connecting them
5. The explanation streams token-by-token over a WebSocket to the React
   dashboard, which draws the connection live on the Cognitive Gap Map

## Real grounding, not free text

Every mistake is tagged with a `concept_key` that maps to an actual,
hand-verified Common Core State Standard pulled from thecorestandards.org —
not an AI guess, not a free-text label someone typed in. This is what lets
two different mistakes about the same idea reliably connect, and it's what
lets us say every diagnosis is grounded in something citable.

## Setup

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
cp .env.example .env           # add your Anthropic API key
uvicorn app.main:app --reload
```
First run downloads the embedding model (`all-MiniLM-L6-v2`, ~80MB).

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Seed demo data
```bash
cd backend
python scripts/seed_demo_data.py
```

## Tools and data disclosure

- **AI tools used:** Claude (Anthropic) — both as the root-cause reasoning
  engine inside the app, and as a coding assistant during development.
  Cursor was used as the editor.
- **Data:** Curriculum data is real Common Core State Standards
  (thecorestandards.org). All student history in the demo is synthetic
  data generated for this project, not real student records.

## Known limitations / what's next

ECHOFORGE currently stops at identifying the root cause — it doesn't yet
generate a follow-up question targeting that misconception, which is the
natural next step. We'd also want a teacher-facing review step before a
diagnosis is shown to a student, since an unchecked AI diagnosis with no
human oversight is a real risk we're not trying to ignore.
