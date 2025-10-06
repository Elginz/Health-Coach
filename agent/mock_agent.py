# This file contains mock (fake) agent logic to speed up development.
# Replace these functions with actual calls to the OpenAI Agent SDK.

def generate_initial_plan(profile):
    """
    Mocks the response for the /goal endpoint.
    """
    print(f"Generating mock plan for profile: {profile.dict()}")
    return {
        "text": "Got it. To lose 10 kg safely over ~4-6 months, here's your starting mock plan.", [cite: 27]
        "cards": [
            {
                "type": "summary",
                "title": "Your Daily Plan",
                "content": "Target ~1500 kcal/day. Focus on low-impact exercise like swimming or brisk walking."
            }
        ],
        "actions": [],
        "trace_id": "mock-trace-123"
    }

def generate_chat_response(message: str):
    """
    Mocks the response for the /chat endpoint.
    """
    print(f"Generating mock response for message: '{message}'")
    # Simple rule-based mock logic
    if "hawker" in message.lower():
        text = "For a hawker meal, try fish soup or a chicken rice set (ask for less rice, no skin). Avoid fried items."
    elif "knee pain" in message.lower():
        text = "I understand. For knee pain, low-impact activities like swimming or cycling are great options." [cite: 45]
    elif "log" in message.lower():
        text = "Progress logged! You're down 1.1 kg. Great job!" [cite: 46]
    else:
        text = "I'm sorry, I can only provide mock responses for now. How else can I help?"

    return {
        "text": text,
        "cards": [],
        "actions": [],
        "trace_id": "mock-trace-456"
    }

# TODO: Create the actual agent files (tools.py, memory.py, safety.py)
# and replace the mock logic in main.py