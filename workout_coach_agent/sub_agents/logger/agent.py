from google.adk.agents import Agent, SequentialAgent
from typing import Dict, Optional, List
from google.adk.tools import ToolContext
from datetime import datetime
from . import prompt
from workout_coach_agent.tools import _make_laravel_request

def _clean_workout_response(response: Dict) -> Dict:
    """
    Cleans up the workout log response to only essential information.

    Args:
        response: Raw API response from workout logging

    Returns:
        Cleaned dictionary with essential workout info including IDs for editing
    """
    if not response.get("success") or not response.get("workout"):
        return response

    workout = response["workout"]

    # Group exercises by name and aggregate their sets, keeping track of IDs
    exercises_summary = {}
    for exercise_entry in workout.get("workout_exercises", []):
        exercise = exercise_entry.get("exercise", {})
        name = exercise.get("name", "Unknown")

        if name not in exercises_summary:
            exercises_summary[name] = {
                "name": name,
                "sets": 0,
                "reps": exercise_entry.get("reps"),
                "weight_kg": exercise_entry.get("weight_kg"),
                "is_pr": False,
                "workout_exercise_id": exercise_entry.get("id"),  # ID of the workout_exercise record
                "exercise_id": exercise.get("id")  # ID of the exercise itself
            }

        exercises_summary[name]["sets"] += 1
        if exercise_entry.get("is_pr"):
            exercises_summary[name]["is_pr"] = True

    return {
        "success": True,
        "message": response.get("message", "Workout logged!"),
        "workout_id": workout.get("id"),  # ID of the workout record
        "workout_date": workout.get("workout_date", "").split("T")[0],
        "total_volume_kg": workout.get("total_volume_kg", 0),
        "exercises": list(exercises_summary.values())
    }

def _get_allowed_exercises() -> List[str]:
    """
    Fetches the list of allowed exercises from the Laravel API.

    Returns:
        List of exercise names that users can log
    """
    try:
        response = _make_laravel_request("GET", "exercises", None)
        # API returns {"exercises": [{"name": "Bench Press", ...}, ...]}
        if isinstance(response, dict) and "exercises" in response:
            return [exercise.get("name") for exercise in response["exercises"] if exercise.get("name")]
        elif isinstance(response, dict) and "data" in response:
            return [exercise.get("name") for exercise in response["data"] if exercise.get("name")]
        elif isinstance(response, list):
            return [exercise.get("name") for exercise in response if exercise.get("name")]
        else:
            print(f"Unexpected response format from exercises API: {response}")
            return []
    except Exception as e:
        print(f"Failed to fetch exercises from API: {e}")
        return []

def get_allowed_exercises() -> Dict:
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
    exercises: List[Dict[str, any]]
) -> Dict:
    """
    Logs one or more workout exercises to the user's training log in a single request.

    Args:
        tool_context: Context containing user_id
        exercises: List of exercise dictionaries, each containing:
            - exercise_name (str): Name of the exercise (e.g., "Bench Press", "Squat")
            - sets (int): Number of sets performed
            - reps (int): Number of repetitions per set
            - weight_kg (float): Weight used in kilograms
            - notes (str, optional): Optional notes about the workout

    Returns:
        Dictionary with confirmation and workout details for all logged exercises

    Examples:
        # Single exercise
        log_workout([
            {"exercise_name": "Bench Press", "sets": 3, "reps": 8, "weight_kg": 60.0, "notes": "Felt great!"}
        ])

        # Multiple exercises
        log_workout([
            {"exercise_name": "Bench Press", "sets": 3, "reps": 8, "weight_kg": 80.0},
            {"exercise_name": "Squat", "sets": 5, "reps": 5, "weight_kg": 100.0},
            {"exercise_name": "Rows", "sets": 3, "reps": 10, "weight_kg": 60.0}
        ])
    """
    user_id = tool_context.state.get("user_id")
    data = {
        "user_id": user_id,
        "exercises": exercises
    }

    response = _make_laravel_request("POST", "workouts/log", data)

    # Clean up the response
    cleaned_response = _clean_workout_response(response)

    # Save to context state with today's date as key
    today = datetime.now().strftime("%Y-%m-%d")
    date_key = f"last_workout_{today}"

    # Check if workout already exists for today
    existing_workout = tool_context.state.get(date_key)

    if existing_workout and existing_workout.get("workout_date") == today:
        # Append exercises to existing workout
        existing_workout["exercises"].extend(cleaned_response["exercises"])
        existing_workout["total_volume_kg"] += cleaned_response["total_volume_kg"]
        tool_context.state[date_key] = existing_workout
        tool_context.state["last_workout"] = existing_workout
        return existing_workout
    else:
        # New day, replace with new workout
        tool_context.state[date_key] = cleaned_response
        tool_context.state["last_workout"] = cleaned_response
        return cleaned_response

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

    This tool now uses the workout_exercise_id from the context state for precise editing,
    making it possible to edit specific exercises even when multiple exercises were logged.

    Args:
        tool_context: Context containing user_id and last workout data
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

    # Try to get the workout_exercise_id from state for more precise editing
    last_workout = tool_context.state.get("last_workout", {})
    workout_exercise_id = None

    if last_workout and "exercises" in last_workout:
        for exercise in last_workout["exercises"]:
            if exercise.get("name", "").lower() == exercise_name.lower():
                workout_exercise_id = exercise.get("workout_exercise_id")
                break

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

    # If we have the workout_exercise_id, include it for precise editing
    if workout_exercise_id:
        data["workout_exercise_id"] = workout_exercise_id

    return _make_laravel_request("PATCH", "workouts/exercises/latest", data)

# Validator agent - validates exercises against approved list
validator_agent = Agent(
    name="validator",
    model="gemini-2.5-flash",
    instruction=_build_validator_instruction(),
    description="Validates that exercises are in the approved list",
    tools=[] 
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
    sub_agents=[validator_agent, recorder_agent],
    description="Validates and logs workouts to database"
)