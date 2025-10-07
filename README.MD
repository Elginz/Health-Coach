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
Dockerfile.backend
Dockefile.frontend
README.md
```
