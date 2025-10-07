# agent/safety.py
from typing import Tuple
import math

def bmi(height_cm: float, weight_kg: float) -> float:
    h_m = height_cm / 100.0
    return round(weight_kg / (h_m * h_m), 2)

def check_red_flags(text: str) -> Tuple[bool, str]:
    """
    Very simple keyword-based red flag detector. Returns (is_red_flag, message)
    """
    t = text.lower()
    red_keywords = ["chest pain", "shortness of breath", "faint", "blackout", "severe abdominal pain", "suicid"]
    for kw in red_keywords:
        if kw in t:
            return True, "Detected red-flag symptom. Advise immediate medical attention / emergency services."
    return False, ""

def validate_target_rate(current_weight: float, target_weight: float, weeks: int = None) -> Tuple[bool, str]:
    """
    Ensures target is not more than ~1kg/week or BMI dropping below 18.5
    """
    kg_to_lose = current_weight - target_weight
    if kg_to_lose <= 0:
        return False, "Target weight must be less than current weight for weight loss."
    # if weeks not provided, assume minimum safe weeks = kg * 1.5 (so rate <= ~0.67 kg/week)
    if weeks:
        rate = kg_to_lose / max(1, weeks)
        if rate > 1.0:
            return False, "Requested pace >1 kg/week — too fast. Pick a slower target."
    # minimal BMI check will be done elsewhere
    return True, ""
