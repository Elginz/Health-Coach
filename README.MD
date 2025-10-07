# WeightCoach — Small Safe Weight-loss Agent

## What this repo contains
- `agent/` — tools, safety checks, memory, and a mock agent that calls the tools.
- `backend/` — FastAPI app exposing `/api/goal`, `/api/chat`, `/api/log`.
- `frontend/` — minimal React/Vite single-page app (Goal form + Chat).
- `data/` — sample data files.
- `Dockerfile` — starts the backend app.

## Quickstart (local)
1. Backend:
```bash
cd <repo-root>
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
python backend/main.py
# API will run at http://localhost:8000


```
agent/
 ├── mock_agent.py     # Mock agent logic (simulated responses)
 ├── tools.py          # Utility functions (TDEE, meal/workout plan, logging)
 ├── safety.py         # BMI & red-flag guardrails
 └── memory.py         # Lightweight memory (SQLite / JSON)

backend/
 ├── main.py           # FastAPI app – routes for /api/goal, /api/chat
 └── requirements.txt  # Python dependencies

frontend/src/
 ├── app.jsx           # React/Vite SPA (Goal form + Chat view)
 └── app.css           # Basic styles

data/
 ├── foods.json        # Sample foods and kcal values
 └── workouts.json     # Sample workouts and durations

Dockerfile
README.md
```
