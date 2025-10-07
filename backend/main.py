# backend/main.py
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import uvicorn
# CORRECTED: This now imports the real 'agent.py' instead of 'mock_agent.py'
from agent import agent, memory
from agent.tools import log_progress
from datetime import datetime
import os

app = FastAPI(title="WeightCoach API")
memory.init_db()

# --- Pydantic Models ---
class Profile(BaseModel):
    age: int
    sex: str
    height_cm: float
    weight_kg: float
    target_weight_kg: float
    activity: str
    conditions: Optional[list] = []
    diet: Optional[str] = ""

class GoalRequest(BaseModel):
    user_id: str
    profile: Profile

class ChatRequest(BaseModel):
    user_id: str
    message: str

# --- API Routes ---
@app.post("/api/goal")
def set_goal(req: GoalRequest):
    profile = req.profile.dict()
    res = agent.handle_goal_request(req.user_id, profile)
    return res

@app.post("/api/chat")
def chat(req: ChatRequest):
    res = agent.handle_chat(req.user_id, req.message)
    return res

# --- Static File Serving ---
STATIC_DIR = "static"
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)
    
app.mount("/assets", StaticFiles(directory=os.path.join(STATIC_DIR, "assets")), name="assets")

@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    index_path = os.path.join(STATIC_DIR, "index.html")
    potential_path = os.path.join(STATIC_DIR, full_path)
    if os.path.isfile(potential_path):
        return FileResponse(potential_path)
    return FileResponse(index_path)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)