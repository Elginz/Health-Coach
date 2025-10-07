import os
import json
from openai import OpenAI
from agent.tools import estimate_tdee, make_meal_plan, make_workout_plan, log_progress
from agent.safety import bmi, check_red_flags, validate_target_rate
from agent import memory

# Initialize the OpenAI client
# It will automatically look for the OPENAI_API_KEY environment variable
try:
    client = OpenAI()
except Exception as e:
    print(f"Error initializing OpenAI client: {e}")
    print("Please make sure the OPENAI_API_KEY environment variable is set.")
    client = None

# --- System Prompt ---
SYSTEM_PROMPT = """
You are AVA, a warm, practical health coach for 1doc. You help adults lose weight safely.
Rules:
- Always be supportive and concise. Use metric units.
- Never diagnose or give medical advice.
- Calories/deficits must be safe (≈500-750 kcal/day).
- CALL THE TOOLS to get information. Do not make up numbers for TDEE, meal plans, or workout plans.
- If information is missing, ask one short clarifying question.
- After calling tools and getting the information, synthesize it into a friendly, helpful response to the user.
"""

# --- Tool Definitions for OpenAI ---
tools = [
    {
        "type": "function",
        "function": {
            "name": "estimate_tdee",
            "description": "Calculates the Total Daily Energy Expenditure (TDEE) and a safe calorie target for a user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "profile": {
                        "type": "object",
                        "description": "User's profile data.",
                        "properties": {
                            "age": {"type": "integer"}, "sex": {"type": "string"},
                            "height_cm": {"type": "number"}, "weight_kg": {"type": "number"},
                            "activity": {"type": "string", "enum": ["sedentary", "light", "moderate", "active", "very"]}
                        },
                        "required": ["age", "sex", "height_cm", "weight_kg", "activity"]
                    }
                },
                "required": ["profile"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "make_meal_plan",
            "description": "Generates a 1-day sample meal plan for a given calorie target.",
            "parameters": {
                "type": "object",
                "properties": {
                    "profile": {"type": "object", "description": "User's profile, including diet or conditions."},
                    "calorie_target": {"type": "integer"}
                },
                "required": ["profile", "calorie_target"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "make_workout_plan",
            "description": "Generates a sample weekly workout plan.",
            "parameters": {
                "type": "object",
                "properties": {"profile": {"type": "object", "description": "User's profile, including conditions like knee pain."}},
                "required": ["profile"]
            }
        }
    }
]

def _run_conversation(messages: list) -> str:
    """Central function to run the conversation with OpenAI, including tool calls."""
    if not client:
        return json.dumps({"text": "OpenAI client not configured. Please set OPENAI_API_KEY.", "cards": [], "actions": []})

    # Step 1: Send the conversation and available functions to the model
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    # Step 2: Check if the model wanted to call a function
    if tool_calls:
        available_functions = {
            "estimate_tdee": estimate_tdee,
            "make_meal_plan": make_meal_plan,
            "make_workout_plan": make_workout_plan,
        }
        messages.append(response_message)  # Extend conversation with assistant's reply

        # Step 3: Call the functions
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call(**function_args)
            
            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": json.dumps(function_response),
            })

        # Step 4: Send the info back to the model a second time
        second_response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
        )
        return second_response.choices[0].message.content
    
    return response_message.content

def handle_goal_request(user_id: str, profile: dict) -> dict:
    """
    Implements /goal contract using the real OpenAI agent.
    """
    # --- Safety Guardrails (Run before calling the AI) ---
    h, w, target = profile.get("height_cm"), profile.get("weight_kg"), profile.get("target_weight_kg")
    
    current_bmi = bmi(h, w)
    if current_bmi < 18.5:
        return {"text": "Your BMI is below 18.5. For safety, I cannot create a weight-loss plan. Please consult a healthcare professional.", "cards": [], "actions": []}

    valid, msg = validate_target_rate(w, target)
    if not valid:
        return {"text": f"Your weight loss target is not recommended: {msg}", "cards": [], "actions": []}

    # --- Construct the prompt for the AI ---
    user_prompt = f"A new user has set a goal. Here is their profile: {json.dumps(profile)}. Please generate a complete starting plan for them by calling the necessary tools."

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]

    # --- Get the AI's response ---
    ai_response_str = _run_conversation(messages)
    
    # The AI should return a JSON object, but we add a fallback
    try:
        final_response = json.loads(ai_response_str)
    except json.JSONDecodeError:
        final_response = {"text": ai_response_str, "cards": [], "actions": []}

    # Store messages in memory
    memory.add_message(user_id, "user", f"Set a goal with profile: {json.dumps(profile)}")
    memory.add_message(user_id, "bot", final_response.get("text", "Here is your plan."))
    
    return final_response


def handle_chat(user_id: str, message: str) -> dict:
    """
    Handles /chat requests using the real OpenAI agent with memory.
    """
    # --- Safety Guardrails (Run before calling the AI) ---
    is_red, flag_msg = check_red_flags(message)
    if is_red:
        return {"text": flag_msg, "cards": [{"type": "safety", "data": {"issue": "red_flag"}}], "actions": []}

    # --- Construct the prompt with memory ---
    history = memory.get_last_messages(user_id, limit=8) # Get last 8 messages for context
    
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in history:
        messages.append({"role": msg["role"], "content": msg["text"]})
    messages.append({"role": "user", "content": message})

    # --- Get the AI's response ---
    ai_response_str = _run_conversation(messages)

    try:
        final_response = json.loads(ai_response_str)
    except json.JSONDecodeError:
        final_response = {"text": ai_response_str, "cards": [], "actions": []}

    # Store the new exchange in memory
    memory.add_message(user_id, "user", message)
    memory.add_message(user_id, "bot", final_response.get("text", "I've received your message."))

    return final_response
