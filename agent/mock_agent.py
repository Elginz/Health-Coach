# agent/mock_agent.py
import json
from datetime import date
from agent.tools import estimate_tdee, make_meal_plan, make_workout_plan, log_progress
from agent.safety import bmi, check_red_flags, validate_target_rate
from agent import memory

def handle_goal_request(user_id: str, profile: dict) -> dict:
    """
    Implements /goal contract. Calls estimate_tdee and returns plan + cards + actions.
    """
    # safety
    h = profile.get("height_cm")
    w = profile.get("weight_kg")
    target = profile.get("target_weight")
    current_bmi = bmi(h, w)
    if current_bmi < 18.5:
        return {
            "text": "BMI indicates underweight or low BMI (<18.5). I cannot create a weight-loss plan; please consult a healthcare professional.",
            "cards": [],
            "actions": [],
            "trace_id": None
        }

    valid, msg = validate_target_rate(w, target)
    if not valid:
        return {
            "text": f"Target not acceptable: {msg}",
            "cards": [],
            "actions": [],
            "trace_id": None
        }

    tdee_res = estimate_tdee(profile)
    # pick midpoint calorie target
    low, high = tdee_res["calorie_target_range"]
    calorie_target = int(round((low + high) / 2))

    meal_plan = make_meal_plan(profile, calorie_target)
    workout_plan = make_workout_plan(profile)

    # store initial message in memory
    memory.add_message(user_id, "user", json.dumps({"event": "set_goal", "profile": profile}))

    text = f"Got it. To lose {int(round(w - target))} kg safely, here's a starting plan with ~{calorie_target} kcal/day target."
    cards = [
        {"type": "tdee", "data": tdee_res},
        {"type": "meal_plan", "data": meal_plan},
        {"type": "workout_plan", "data": workout_plan}
    ]
    actions = [
        {"type": "action", "label": "Start 1-day meal plan", "payload": {"action": "apply_meal_plan", "calorie_target": calorie_target}},
        {"type": "action", "label": "Log today's weight", "payload": {"action": "prompt_log_weight"}}
    ]
    return {
        "text": text,
        "cards": cards,
        "actions": actions,
        "trace_id": tdee_res.get("trace_id")
    }

def handle_chat(user_id: str, message: str) -> dict:
    # check red flags
    is_red, message_flag = check_red_flags(message)
    if is_red:
        return {
            "text": "I detected a possible medical emergency in your message. I can't handle emergencies — please seek immediate medical attention or call your local emergency number.",
            "cards": [{"type": "safety", "data": {"issue": "red_flag", "message": message_flag}}],
            "actions": [{"type": "escalate", "label": "Call emergency services", "payload": {}}],
            "trace_id": None
        }

    # naive intent: if contains 'eat' or 'hawker' -> meal swaps
    lower = message.lower()
    if "hawker" in lower or "eat tomorrow" in lower or "what should i eat" in lower:
        # assume we need tdee for user; fetch last message to parse profile (demo approach)
        last = memory.get_last_messages(user_id)
        # fallback demo profile
        profile = {"age": 61, "sex": "F", "height_cm": 158, "weight_kg": 72, "activity": "light", "diet": "no_pork", "conditions": ["type2_diabetes"]}
        # call TDEE if we had profile saved; else use fallback
        tdee = estimate_tdee(profile)
        cal_low, cal_high = tdee["calorie_target_range"]
        # return suggestions with swap options
        text = f"For a ~{int(round((cal_low+cal_high)/2))} kcal/day target, choose hawker swaps around 400-700 kcal per meal depending on meal."
        cards = [{
            "type": "hawker_swaps",
            "data": {
                "meal_examples": [
                    {"name": "Chicken rice (small serving + veg)", "kcal": 600, "swap": "Replace chicken skin with extra veg; choose brown rice portion"},
                    {"name": "Fish soup + rice (small)", "kcal": 450, "swap": "Ask for less oil; add extra veg"},
                    {"name": "Yong tau foo (no fried items)", "kcal": 350, "swap": "Avoid fried beancurd; choose broth"}
                ],
                "kcal_range_per_meal": [400, 700]
            }
        }]
        return {"text": text, "cards": cards, "actions": [], "trace_id": tdee["trace_id"]}

    # default: echo supportive coaching + nudge
    memory.add_message(user_id, "user", message)
    # short coaching reply
    reply = "Nice — small consistent steps work best. Try a 30-min walk today and choose a vegetable-heavy meal. Want a 1-day meal plan?"
    memory.add_message(user_id, "bot", reply)
    return {"text": reply, "cards": [], "actions": [{"type": "ask", "label": "Get 1-day meal plan", "payload": {"action": "get_meal_plan"}}], "trace_id": None}
