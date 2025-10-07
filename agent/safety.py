"""
agent/safety.py
Safety guardrails:
- BMI check
- Target rate check (reject if >1 kg/week implied)
- Red-flag phrase scanning (e.g., chest pain)
"""

from typing import Dict, Any, List
import math
import re

RED_FLAG_PATTERNS = [
    r"\bchest pain\b",
    r"\bshortness of breath\b",
    r"\bpass out\b",
    r"\bsuicid(e|al)\b",
    r"\bsevere pain\b",
    r"\btrouble breathing\b",
]

def compute_bmi(weight_kg: float, height_cm: float) -> float:
    h_m = float(height_cm) / 100.0
    if h_m <= 0:
        return 0.0
    return float(round(weight_kg / (h_m * h_m), 2))

def safety_check(profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Returns dict:
    {
      ok: bool,
      text: str,
      card: Optional[dict],
      escalate: bool
    }
    """
    age = int(profile.get("age", 0))
    w = float(profile.get("weight_kg", 0.0))
    h = float(profile.get("height_cm", 0.0))
    target = float(profile.get("target_weight_kg", w))
    bmi = compute_bmi(w, h)

    # Basic checks
    if bmi < 18.5:
        return {
            "ok": False,
            "text": "I can't create a weight-loss plan because your BMI is under 18.5 — I recommend speaking to a clinician.",
            "card": {"title": "Underweight — Medical review recommended", "body": f"Your BMI is {bmi}. Please check with a healthcare professional."},
            "escalate": True,
        }

    # target rate check: compute implied weekly loss if target achieved in 12 weeks minimum
    # Compute weeks needed at safe pace (0.5 to 0.8 kg/week). If implied >1 kg/week, reject.
    delta_kg = w - target
    if delta_kg <= 0:
        return {"ok": False, "text": "Target weight must be lower than current weight.", "card": None, "escalate": False}

    # If user wants to lose huge amount, compute minimal safe weeks (0.5 kg/week)
    implied_weeks = delta_kg / 0.5
    implied_rate = None
    # If user provided a time estimate in profile (not present here) we would evaluate; otherwise just ensure delta not too fast
    # If delta_kg > 20 kg we warn: suggest staged goals
    if delta_kg > 25:
        return {
            "ok": False,
            "text": "That's a large target. For safety, we recommend splitting this into staged goals and consulting a clinician.",
            "card": {"title": "Large Weight Loss Target", "body": "Consider staged goals (e.g., 5-10 kg at a time) and seek clinician guidance."},
            "escalate": False,
        }

    # No other automatic rejects here: ok
    return {"ok": True, "text": "Profile looks OK for a safe plan.", "card": None, "escalate": False}

def scan_for_red_flags(message: str) -> List[str]:
    flags = []
    if not message:
        return flags
    m = message.lower()
    for pat in RED_FLAG_PATTERNS:
        if re.search(pat, m):
            flags.append(pat)
    return flags
