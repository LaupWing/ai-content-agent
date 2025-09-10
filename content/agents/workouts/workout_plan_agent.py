from google.adk.agents import Agent

# --- Placeholder tools ---

def get_today_plan(date: str = "2025-09-10") -> dict:
    """Return a fake workout plan for today (placeholder)."""
    return {
        "status": "success",
        "plan": [
            {"exercise": "Bench Press", "sets": 3, "reps": 10},
            {"exercise": "Squats", "sets": 4, "reps": 8},
            {"exercise": "Plank", "duration": "3 x 60s"},
        ],
        "note": f"Plan for {date}"
    }

def get_full_plan(weeks: int = 1) -> dict:
    """Return a fake full workout plan (placeholder)."""
    return {
        "status": "success",
        "plan": {
            "Day 1": ["Bench Press", "Squats", "Plank"],
            "Day 2": ["Deadlift", "Pull-ups", "Plank"],
            "Day 3": ["Rest"],
            "Day 4": ["Overhead Press", "Lunges", "Sit-ups"],
        },
        "note": f"{weeks}-week placeholder plan"
    }

# --- Agent definition ---

workout_plan_agent = Agent(
    name="workout_plan_agent",
    model="gemini-2.0-flash",
    description="Provides workout plans for today or for a full schedule.",
    instruction=(
        "You are a workout planner.\n"
        "- If the user asks for today's workout (e.g., 'what do I do today?'), call the tool 'get_today_plan'.\n"
        "- If the user asks for the whole plan (week/month/etc.), call the tool 'get_full_plan'.\n"
        "Always present the results clearly and concisely."
    ),
    tools=[get_today_plan, get_full_plan],
)
