"""
agent/tools.py
Concrete implementations of the agent tools:
- estimate_tdee(profile) -> dict
- make_meal_plan(profile, calorie_target) -> dict
- make_workout_plan(profile) -> dict
- log_progress(user_id, date, weight_kg) -> dict

This module reads sample data from ../data/*.json and uses agent.memory to persist weight logs.
"""
from __future__ import annotations
import json
import math
from pathlib import Path
from typing import Dict, Any, List
from datetime import date, datetime

from agent import memory

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

# activity factor map (Mifflin-St Jeor * activity)
_ACTIVITY_FACTORS = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
    "very_active": 1.9,
}

def _load_json(fname: str):
    p = DATA_DIR / fname
    if not p.exists():
        return {}
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

FOODS = _load_json("foods.json")
WORKOUTS = _load_json("workouts.json")

def estimate_tdee(profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Estimate BMR (Mifflin-St Jeor) then TDEE.
    profile keys: age, sex, height_cm, weight_kg, activity
    Returns: {bmr, tdee, activity_factor, recommended_deficit_kcal, safe_range}
    """
    sex = profile.get("sex", "F").lower()
    age = int(profile["age"])
    h = float(profile["height_cm"])
    w = float(profile["weight_kg"])

    # Mifflin-St Jeor
    # men: BMR = 10*w + 6.25*h - 5*age + 5
    # women: BMR = 10*w + 6.25*h - 5*age - 161
    if sex.startswith("m"):
        bmr = 10.0 * w + 6.25 * h - 5.0 * age + 5.0
    else:
        bmr = 10.0 * w + 6.25 * h - 5.0 * age - 161.0

    activity = profile.get("activity", "light").lower()
    activity_factor = _ACTIVITY_FACTORS.get(activity, _ACTIVITY_FACTORS["light"])
    tdee = int(round(bmr * activity_factor))

    # safe deficit: 500-750 kcal/day (enforced elsewhere)
    recommended_deficit_kcal = 600

    # minimum calorie floor heuristics
    minimum_cal = 1200 if sex.startswith("f") else 1500

    # recommended calorie target (clamped)
    suggested = max(minimum_cal, tdee - recommended_deficit_kcal)

    return {
        "bmr": int(round(bmr)),
        "tdee": tdee,
        "activity_factor": activity_factor,
        "recommended_deficit_kcal": recommended_deficit_kcal,
        "calorie_target_suggestion": int(round(suggested)),
        "minimum_calorie_floor": minimum_cal,
    }

def make_meal_plan(profile: Dict[str, Any], calorie_target: int) -> Dict[str, Any]:
    """
    Simple meal plan generator using foods.json. Returns one-day sample + macros heuristics.
    Respects simple diet restrictions and T2DM note (keep lower glycemic carbs).
    """
    diet = (profile.get("diet") or "").lower()
    conditions = [c.lower() for c in (profile.get("conditions") or [])]

    # Very simple macro splits
    weight_kg = float(profile["weight_kg"])
    protein_g = int(round(1.2 * weight_kg))  # g protein/day
    fat_pct = 0.25
    fat_kcal = calorie_target * fat_pct
    fat_g = int(round(fat_kcal / 9.0))
    carbs_kcal = calorie_target - (protein_g * 4) - (fat_g * 9)
    carbs_g = max(0, int(round(carbs_kcal / 4.0)))

    # pick foods from FOODS - try breakfast/lunch/dinner
    def pick(list_key: str) -> Dict[str, Any]:
        items = FOODS.get(list_key, [])
        if not items:
            return {}
        # pick first that matches diet constraints
        for it in items:
            name = it.get("name", "").lower()
            tags = [t.lower() for t in it.get("tags", [])] if it.get("tags") else []
            if diet and diet in name:
                continue
            if diet and "no_pork" in diet and ("pork" in name or "char siew" in name):
                continue
            # For diabetes, prefer non-fried
            if "type2" in " ".join(conditions) and ("fried" in name or "sugar" in name):
                continue
            return it
        return items[0]  # fallback

    breakfast = pick("breakfast")
    lunch = pick("lunch")
    dinner = pick("dinner")
    snack = {"name": "Greek yogurt (small)", "kcal": 120}

    summary = {
        "calorie_target": calorie_target,
        "macros": {"protein_g": protein_g, "fat_g": fat_g, "carbs_g": carbs_g},
        "meals": [
            {"slot": "breakfast", **(breakfast or {})},
            {"slot": "lunch", **(lunch or {})},
            {"slot": "dinner", **(dinner or {})},
            {"slot": "snack", **snack},
        ],
        "notes": "Focus on portion size, protein at each meal, lower glycemic carbs if you have diabetes.",
    }
    return summary

def make_workout_plan(profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Make a weekly workout plan using workouts.json, adjust for knee/back issues via 'conditions'.
    """
    conditions = [c.lower() for c in (profile.get("conditions") or [])]
    knee_pain = any("knee" in c or "knee pain" in c for c in conditions)

    if knee_pain:
        # prefer low impact activities
        plan = [
            {"day": "Mon", "activity": "Swimming or pool walking", "duration_mins": 30},
            {"day": "Tue", "activity": "Upper-body strength + mobility", "duration_mins": 25},
            {"day": "Wed", "activity": "Rest / gentle stretching", "duration_mins": 20},
            {"day": "Thu", "activity": "Cycling (stationary) or elliptical", "duration_mins": 30},
            {"day": "Fri", "activity": "Full-body strength (no deep squats)", "duration_mins": 30},
            {"day": "Sat", "activity": "Walk (brisk) or swim", "duration_mins": 30},
            {"day": "Sun", "activity": "Mobility & foam rolling", "duration_mins": 20},
        ]
    else:
        # use sample workouts list, rotate
        plan = [
            {"day": "Mon", "activity": "Brisk Walking", "duration_mins": 30},
            {"day": "Tue", "activity": "Bodyweight Circuit", "duration_mins": 25},
            {"day": "Wed", "activity": "Light Jog or Bike", "duration_mins": 25},
            {"day": "Thu", "activity": "Strength (bodyweight)/mobility", "duration_mins": 30},
            {"day": "Fri", "activity": "Brisk Walk or Swim", "duration_mins": 30},
            {"day": "Sat", "activity": "Active recovery / yoga", "duration_mins": 20},
            {"day": "Sun", "activity": "Rest", "duration_mins": 0},
        ]

    return {
        "summary": "Weekly plan, adjust intensity as needed. Prioritise consistency over intensity.",
        "plan": plan,
    }

def log_progress(user_id: str, date_str: str, weight_kg: float) -> Dict[str, Any]:
    """
    Persist weight log using agent.memory and return progress summary (delta vs previous).
    date_str in 'YYYY-MM-DD' preferable. If not provided, uses today's date.
    """
    if not date_str:
        date_str = date.today().isoformat()
    db = memory.Memory()  # uses ../data/coach.db
    prev = db.get_last_weight(user_id)
    db.log_weight(user_id, date_str, weight_kg)
    delta = None
    if prev is not None:
        delta = float(round(weight_kg - prev, 2))
    summary = {
        "user_id": user_id,
        "date": date_str,
        "weight_kg": float(weight_kg),
        "delta_since_prev_kg": delta,
        "note": "Logged",
    }
    return summary
