from google.adk.agents import Agent
from typing import Dict, Optional, List
from google.adk.tools import ToolContext
from . import prompt
from workout_coach_agent.tools import _make_laravel_request

def _get_allowed_exercises() -> List[str]:
    """
    Fetches the list of allowed exercises from the Laravel API.

    Returns:
        List of exercise names that users can log
    """
    try:
        response = _make_laravel_request("GET", "exercises", None)
        # Assuming the API returns {"data": [{"name": "Bench Press", ...}, ...]}
        # Adjust the parsing based on your actual API response structure
        if isinstance(response, dict) and "data" in response:
            return [exercise.get("name") for exercise in response["data"] if exercise.get("name")]
        elif isinstance(response, list):
            return [exercise.get("name") for exercise in response if exercise.get("name")]
        else:
            print(f"Unexpected response format from exercises API: {response}")
            return []
    except Exception as e:
        print(f"Failed to fetch exercises from API: {e}")
        return []

def _build_logger_instruction() -> str:
    """
    Builds the logger agent instruction with dynamically fetched exercises.

    Returns:
        Complete instruction string with allowed exercises list
    """
    allowed_exercises = _get_allowed_exercises()

    base_instruction = prompt.LOGGER_PROMPT

    if allowed_exercises:
        exercises_list = "\n".join([f"    - {exercise}" for exercise in allowed_exercises])
        exercise_constraint = f"""
            ## IMPORTANT: Exercise Validation

            You MUST ONLY log exercises from this approved list. Focus on the basics - consistency matters more than variety.

            **Allowed Exercises:**
            {exercises_list}

            **Validation Rules:**
            - If the user mentions an exercise NOT on this list, politely inform them it's not in the approved exercise list
            - Suggest the closest matching exercise from the approved list
            - DO NOT log exercises that aren't on this list
            - The exercise name must match EXACTLY (case-insensitive) with one from the approved list

            **Example Response for Invalid Exercise:**
            User: "I did tricep kickbacks 3x12 at 10kg"
            You: "Tricep kickbacks isn't in your approved exercise list. Did you mean Tricep Extensions or Dips? Here are the allowed exercises for triceps: [list relevant exercises]"
        """
        return base_instruction + exercise_constraint
    else:
        # Fallback if API fails
        return base_instruction

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
            "exercise_name": exercise_name,
            "sets": sets,
            "reps": reps,
            "weight_kg": weight_kg,
            "notes": notes,
        }
    }

    return _make_laravel_request("POST", "workouts/log", data)

def edit_latest_exercise(
    tool_context: ToolContext,
    exercise_name: str,
    sets: Optional[int] = None,
    reps: Optional[int] = None,
    weight_kg: Optional[float] = None,
    notes: Optional[str] = None
) -> Dict:
    """
    Edits the most recent logged instance of a specific exercise.

    Use this when the user wants to correct their latest workout entry for a specific exercise.
    For example: "bench press was 110kg not 105kg" or "actually I did 4 sets of squats"

    Args:
        tool_context: Context containing user_id
        exercise_name: Name of the exercise to edit (e.g., "Bench Press", "Squat")
        sets: New number of sets (optional, only updates if provided)
        reps: New number of reps (optional, only updates if provided)
        weight_kg: New weight in kilograms (optional, only updates if provided)
        notes: New notes (optional, only updates if provided)

    Returns:
        Dictionary with updated exercise details

    Example:
        edit_latest_exercise("Bench Press", weight_kg=110.0)
    """
    user_id = tool_context.state.get("user_id")

    # Build updates dictionary with only provided values
    updates = {}
    if sets is not None:
        updates["sets"] = sets
    if reps is not None:
        updates["reps"] = reps
    if weight_kg is not None:
        updates["weight_kg"] = weight_kg
    if notes is not None:
        updates["notes"] = notes

    data = {
        "user_id": user_id,
        "exercise_name": exercise_name,
        "updates": updates
    }

    return _make_laravel_request("PATCH", "workouts/exercises/latest", data)

logger = Agent(
    name="logger",
    model="gemini-2.5-flash",
    instruction=_build_logger_instruction(),
    description="Parses natural language and logs workouts to database",
    tools=[log_workout, edit_latest_exercise]
)