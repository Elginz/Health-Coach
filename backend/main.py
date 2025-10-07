# backend/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn
from agent import mock_agent, memory
from agent.tools import log_progress
from datetime import datetime

app = FastAPI(title="WeightCoach API")
memory.init_db()

class Profile(BaseModel):
    age: int
    sex: str
    height_cm: float
    weight_kg: float
    target_weight: float
    activity: str
    conditions: Optional[list] = []
    diet: Optional[str] = ""

class GoalRequest(BaseModel):
    user_id: str
    profile: Profile

class ChatRequest(BaseModel):
    user_id: str
    message: str

class LogRequest(BaseModel):
    user_id: str
    date: Optional[str] = None  # ISO date or YYYY-MM-DD
    weight_kg: float

@app.post("/api/goal")
def set_goal(req: GoalRequest):
    profile = req.profile.dict()
    res = mock_agent.handle_goal_request(req.user_id, profile)
    if res.get("trace_id") is None and len(res.get("cards", [])) == 0:
        # likely safety rejection
        return res
    # persist an initial bot response in memory
    memory.add_message(req.user_id, "bot", res["text"])
    return res

@app.post("/api/chat")
def chat(req: ChatRequest):
    res = mock_agent.handle_chat(req.user_id, req.message)
    # store chat in memory if not a red-flag (already stored inside)
    return res

@app.post("/api/log")
def log(req: LogRequest):
    dt = req.date or datetime.utcnow().strftime("%Y-%m-%d")
    # persist via memory + tools (tools returns simple response)
    memory.add_message(req.user_id, "user", f"log {req.weight_kg}kg on {dt}")
    memory.add_message(req.user_id, "bot", f"Logged weight {req.weight_kg} kg")
    tool_res = log_progress(dt, req.weight_kg, req.user_id)
    return {
        "text": f"Logged {req.weight_kg} kg on {dt}.",
        "cards": [{"type": "progress_log", "data": {"date": dt, "weight": req.weight_kg}}],
        "actions": [],
        "trace_id": tool_res.get("trace_id")
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
