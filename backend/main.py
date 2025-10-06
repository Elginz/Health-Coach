from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import List, Optional

# Mock agent functions for now
from agent import mock_agent

# --- Pydantic Models for API Contracts ---
class UserProfile(BaseModel):
    age: int [cite: 22]
    sex: str [cite: 22]
    height_cm: int [cite: 22]
    weight_kg: float [cite: 22]
    target_weight_kg: float [cite: 22]
    activity: str [cite: 23]
    conditions: Optional[List[str]] = [] [cite: 23]
    diet: Optional[str] = None [cite: 23]

class GoalRequest(BaseModel):
    user_id: str [cite: 21]
    profile: UserProfile [cite: 22]

class ChatRequest(BaseModel):
    user_id: str
    message: str

# --- FastAPI App ---
app = FastAPI()

@app.post("/api/goal")
def set_goal(request: GoalRequest):
    """
    Handles the initial goal setting from the user profile form.
    """
    # TODO: Replace with actual call to the OpenAI agent
    # The agent would use estimate_tdee, make_meal_plan, etc.
    return mock_agent.generate_initial_plan(request.profile)

@app.post("/api/chat")
def chat(request: ChatRequest):
    """
    Handles subsequent chat messages from the user.
    """
    # TODO: Replace with actual call to the OpenAI agent
    # The agent would use its tool-calling ability based on the message
    return mock_agent.generate_chat_response(request.message)


# --- Static File Serving for Frontend ---
app.mount("/assets", StaticFiles(directory="static/assets"), name="assets")

@app.get("/")
async def read_index():
    return FileResponse('static/index.html')

@app.get("/{catchall:path}", response_class=FileResponse)
def read_static_files(catchall: str):
    # This is a fallback to ensure client-side routing works with React Router
    return FileResponse('static/index.html')