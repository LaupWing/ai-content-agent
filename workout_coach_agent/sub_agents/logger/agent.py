from google.adk.agents import Agent, SequentialAgent
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

def get_allowed_exercises(tool_context: ToolContext) -> Dict:
    """
    Tool to fetch and return the list of allowed exercises.

    Returns:
        Dictionary containing the allowed exercises list
    """
    exercises = _get_allowed_exercises()
    return {
        "allowed_exercises": exercises,
        "count": len(exercises)
    }

def _build_validator_instruction() -> str:
    """
    Builds the validator agent instruction with dynamically fetched exercises.

    Returns:
        Instruction string for the validator agent
    """
    allowed_exercises = _get_allowed_exercises()

    if allowed_exercises:
        exercises_list = "\n".join([f"    - {exercise}" for exercise in allowed_exercises])
        return f"""
You are an exercise validator. Your job is to verify that exercises mentioned by the user are in the approved exercise list.

## Allowed Exercises:
{exercises_list}

## Your Responsibilities:

1. **Parse the user's workout description** to extract all exercise names mentioned
2. **Validate each exercise** against the approved list (case-insensitive matching)
3. **If ALL exercises are valid**: Extract and structure the workout data (exercise, sets, reps, weight, notes) and pass it forward
4. **If ANY exercise is invalid**:
   - Inform the user which exercise(s) are not approved
   - Suggest the closest matching exercise from the approved list
   - DO NOT proceed with logging - stop here and ask the user to correct

## Output Format:

**For valid exercises**, respond with structured data:
```
VALID: <exercise_name> | <sets> | <reps> | <weight_kg> | <notes>
```

**For invalid exercises**, respond:
```
INVALID: <exercise_name> is not in the approved list. Did you mean <closest_match>?
Approved exercises: [list relevant ones]
```

Focus on the basics - consistency matters more than variety.
"""
    else:
        return "You are an exercise validator. Validate exercises against the approved list using the get_allowed_exercises tool."

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

# Validator agent - validates exercises against approved list
validator_agent = Agent(
    name="validator",
    model="gemini-2.5-flash",
    instruction=_build_validator_instruction(),
    description="Validates that exercises are in the approved list",
    tools=[]  # No tools needed, validation is done in the instruction
)

# Recorder agent - logs validated workouts to database
recorder_agent = Agent(
    name="recorder",
    model="gemini-2.5-flash",
    instruction=prompt.LOGGER_PROMPT,
    description="Records validated workout data to database",
    tools=[log_workout, edit_latest_exercise]
)

# Main logger as SequentialAgent - validator first, then recorder
logger = SequentialAgent(
    name="logger",
    model="gemini-2.5-flash",
    instruction="You coordinate workout logging by first validating exercises, then recording them.",
    description="Validates and logs workouts to database",
    agents=[validator_agent, recorder_agent]
)