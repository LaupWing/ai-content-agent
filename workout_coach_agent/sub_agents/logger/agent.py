from google.adk.agents import Agent
from typing import Dict, Optional
from google.adk.tools import ToolContext
from . import prompt 
from tools import _make_laravel_request

def log_workout(
    tool_context: ToolContext,
    exercise_name: str,
    sets: int,
    reps: int,
    weight_kg: float,
    notes: Optional[str] = None
) -> Dict:
    """
    Logs a workout exercise to the user's training log.
    
    Args:
        user_id: The user's database ID
        exercise_name: Name of the exercise (e.g., "Bench Press", "Squat")
        sets: Number of sets performed
        reps: Number of repetitions per set
        weight_kg: Weight used in kilograms
        notes: Optional notes about the workout (e.g., "Felt strong", "Lower back tight")
    
    Returns:
        Dictionary with confirmation and workout details
    
    Example:
        log_workout(2, "Bench Press", 3, 8, 60.0, "Felt great!")
    """
    user_id = tool_context.state.get("user_id")
    data = {
        "user_id": user_id,
        "workout_data": {
            "exercises": [{
                "name": exercise_name,
                "sets": sets,
                "reps": reps,
                "weight_kg": weight_kg,
                "notes": notes,
            }]
        }
    }
    
    return _make_laravel_request("POST", "workouts/log", data)

logger = Agent(
    name="logger",
    model="gemini-2.5-flash",
    instruction=prompt.LOGGER_PROMPT,
    description="Parses natural language and logs workouts to database",
    tools=[log_workout]
)