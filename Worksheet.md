# Goal 
To Ship a small web app where user chats with BOT, Sets a weight-loss goal (-10kg), and receives a safe, personalised plan with daily nudges. Backend uses OpenAI Agent SDK with a few callable tools. 

# Success Criteria
1. Web UI(Single page app): Chat panle. "Set Goal" form (current weight, taret weight, height, age, sex, activity level) and a "Today" Card with nudges
2. Backend (Python FastAPI or Node/Express): Uses OpenAI Agent SDK / Responses API with tool calling
3. Tools implemented: estimat_tdee, make_meal_plan, make_workoout_plan, log_progress.
4.Safety guardrails: Red flag and BMI checks with escalation logic.
5. State & memory: Last 10 message per user in SQLite / JSON
6. Dockerized with a clear README

# System Prompt
You are BOT , a warm, practical health coach for company A. You help adults lose weight safely. 
Rules:
- Always be supportive and concise, Use metric units 
- Never Diagnose or give Medical advice
- Calores/deficits must be safe (500-750 kcal)/day
- CALL THE TOOLS: estimate_tdee, make_meal_plan, make_workout_plan, log_progress
- Output JSON: {text, cards[],actions[],trace_id}
- if information is missing,ask one short clarifying question

API Contracts
Request: /goal
{
"user_id" :"demo",
"profile":{"age": 61, "sex": "F", "height_cm": 158,"weight_kg" :72,"target_weight": 62,"activity": "light","conditions": [type2_diabetes], "diet":"no_pork"}
}

Response: /goal
{
"text": "Got it. To lose 10kg safely over ~4-6 months, here's your starting plan.",
"cards": [...],
"actions": [...],
"trace_id":"..."
}

# Tool signatures
estimate_tdee(profile) dict
make_meal_plan(profile, calorie_target) dict
make_workout_plan(profile) dict
log_progress(date, weight) dict

# Front-end spec
stack: React or Vite + fetch
Views:
1. Goal Setup Form (/goal)
2. Chat(/chat) -render messages and cards
3. Progress Widget - log and visualize weight

# Test Cases
1. input: 61F, 158cm, 62kg, light activity, T2DM safe plan (~1500 kcal, 0.5-0.8 kg/week)
2. Query: "What should i eat tomorrow at hawker" get swaps and kcal range
3. Query: "I have Knee pain, what can i do?" Low impact plan
4. Log: "log 70.9kg" Progress card with -1.1kg in 2 weeks.

# Red Flag Tests
User: "I have Chest Pain" Safety Card + escalate
BMI < 18.5 or target >1kg/week reject with caution

# Evaluation Rubric (20 pts)
- Docker + README:3
- Agent SDK + Tool use: 5
- SafeCoaching Logic: 4
- UI Rendering: 3
- Memory: 2
- Progress Feedback: 2
- Code Quality: 1
Bonus: +4 for auth, rate-limit, tests. /metrics


# Project Structure
/ frontend (React/Vite)

/ backend (FastAPI)

/ agent (tools, memory. safety)

/ data (foods.json, workouts.json)

README.md
Dockerfile
