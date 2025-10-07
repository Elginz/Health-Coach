# agent/tools.py
import math
import uuid
from datetime import date, datetime

def estimate_tdee(profile: dict) -> dict:
    """
    Mifflin-St Jeor, metric. activity: sedentary, light, moderate, active, very
    Returns dict with tdee, maintenance_kcal, recommended_loss_kcal (safe deficit 500-750)
    """
    age = profile.get("age")
    sex = profile.get("sex", "F").lower()
    h = profile.get("height_cm")
    w = profile.get("weight_kg")
    activity = profile.get("activity", "light").lower()

    if None in (age, h, w):
        raise ValueError("missing profile fields for TDEE")

    # BMR
    if sex.startswith("m"):
        bmr = 10 * w + 6.25 * h - 5 * age + 5
    else:
        bmr = 10 * w + 6.25 * h - 5 * age - 161

    activity_factors = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very": 1.9
    }
    af = activity_factors.get(activity, 1.375)
    tdee = int(round(bmr * af))

    # safe deficit
    deficit_low = 500
    deficit_high = 750
    calorie_target_low = max(1200, tdee - deficit_high)  # never below 1200
    calorie_target_high = max(1200, tdee - deficit_low)

    return {
        "trace_id": str(uuid.uuid4()),
        "bmr": int(round(bmr)),
        "tdee": tdee,
        "calorie_target_range": [calorie_target_low, calorie_target_high],
        "safe_deficit": [deficit_low, deficit_high],
        "generated_at": datetime.utcnow().isoformat() + "Z"
    }


def make_meal_plan(profile: dict, calorie_target: int) -> dict:
    """
    Returns a simple 1-day meal plan (breakfast/lunch/dinner+snacks).
    Uses data/foods.json ideally; here simple canned swaps and totals.
    """
    # Basic sample templates; in production load foods.json
    sex = profile.get("sex")
    diet = profile.get("diet", "")
    conditions = profile.get("conditions", [])

    # Simple rationing: 25% breakfast, 35% lunch, 30% dinner, 10% snacks
    b = int(round(calorie_target * 0.25))
    l = int(round(calorie_target * 0.35))
    d = int(round(calorie_target * 0.30))
    s = calorie_target - (b + l + d)

    plan = {
        "trace_id": str(uuid.uuid4()),
        "calorie_target": calorie_target,
        "meals": {
            "breakfast": {
                "suggestion": f"Oats with milk + banana (≈{b} kcal)",
                "kcal": b,
                "notes": "High fibre; swap banana for berries if preferred"
            },
            "lunch": {
                "suggestion": f"Grilled chicken salad + brown rice (≈{l} kcal)",
                "kcal": l,
                "notes": "Use low oil dressing; extra veg for volume"
            },
            "dinner": {
                "suggestion": f"Tofu/lean fish + steamed veg + small sweet potato (≈{d} kcal)",
                "kcal": d,
                "notes": "Low-salt for diabetes; avoid large sauces"
            },
            "snack": {
                "suggestion": f"Greek yogurt or a small handful nuts (≈{s} kcal)",
                "kcal": s
            }
        },
        "suitable_for": {
            "diet_notes": "no_pork" if "no_pork" in diet else "standard",
            "conditions": conditions
        },
        "generated_at": datetime.utcnow().isoformat() + "Z"
    }
    return plan


def make_workout_plan(profile: dict) -> dict:
    """
    Return a simple weekly low / moderate impact plan based on activity and conditions.
    """
    activity = profile.get("activity", "light")
    conditions = profile.get("conditions", [])
    knee = any("knee" in str(c).lower() for c in conditions)

    # Sample
    plan = {
        "trace_id": str(uuid.uuid4()),
        "summary": "Mix of low-impact cardio + strength + mobility",
        "weeks": []
    }

    # Week template
    week = [
        {"day": "Mon", "activity": "Brisk walk or treadmill 30-40 min (low impact)"},
        {"day": "Tue", "activity": "Bodyweight strength 20-30 min (squats, push, hinge)"},
        {"day": "Wed", "activity": "Active recovery: gentle yoga / mobility 20-30 min"},
        {"day": "Thu", "activity": "Cycling or elliptical 30-40 min (low impact)"},
        {"day": "Fri", "activity": "Strength 20-30 min (light weights)"},
        {"day": "Sat", "activity": "Optional walk or swim 30-45 min"},
        {"day": "Sun", "activity": "Rest / stretch"}
    ]

    if knee:
        # replace high-knee moves
        for item in week:
            item["activity"] = item["activity"].replace("run", "walk").replace("squats", "chair squats / glute bridges")

    plan["weeks"].append({"week_number": 1, "days": week})
    plan["notes"] = "If any pain or chest pain occurs, stop and seek medical help. Low-impact recommended for joint issues."
    plan["generated_at"] = datetime.utcnow().isoformat() + "Z"
    return plan


def log_progress(date_str: str, weight: float, user_id: str = "demo") -> dict:
    """Simple log response — actual persistence handled by memory module"""
    return {
        "trace_id": str(uuid.uuid4()),
        "logged": True,
        "date": date_str,
        "weight": weight,
        "user_id": user_id,
        "ts": datetime.utcnow().isoformat() + "Z"
    }
