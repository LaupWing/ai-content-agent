from google.adk.agents import Agent
from typing import Dict, Optional
from google.adk.tools import ToolContext
from . import prompt
from workout_coach_agent.tools import _make_laravel_request


def edit_workout(
    tool_context: ToolContext,
    exercise_name: str,
    sets: Optional[int] = None,
    reps: Optional[int] = None,
    weight_kg: Optional[float] = None,
    notes: Optional[str] = None
) -> Dict:
    """
    Edits a workout exercise from today's session.

    IMPORTANT: Only call this function when the user explicitly wants to EDIT/CORRECT an existing exercise.
    Do NOT call this for new workout entries - use log_workout for new entries.

    Use this when the user wants to correct an exercise they already logged today:
    - "bench press was 110kg not 105kg"
    - "actually I did 4 sets of squats"
    - "change the bench to 100kg"

    This tool uses the workout_exercise_id from context state for precise editing.

    Args:
        tool_context: Context containing user_id and last workout data
        exercise_name: Name of the exercise to edit (e.g., "Bench Press", "Squat")
        sets: New number of sets (optional, only include if changing)
        reps: New number of reps (optional, only include if changing)
        weight_kg: New weight in kilograms (optional, only include if changing)
        notes: New notes (optional, only include if changing)

    Returns:
        Dictionary with updated exercise details

    Example:
        # User says: "bench was 120kg not 110kg"
        edit_workout("Bench Press", weight_kg=120.0)

        # User says: "actually did 4 sets of squats"
        edit_workout("Squats", sets=4)
    """
    user_id = tool_context.state.get("user_id")

    # Get all workout_exercise_ids for the named exercise from state
    last_workout = tool_context.state.get("last_workout", {})
    workout_exercise_ids = []

    if last_workout and "exercises" in last_workout:
        for exercise in last_workout["exercises"]:
            if exercise.get("name", "").lower() == exercise_name.lower():
                workout_exercise_ids.append(exercise.get("workout_exercise_id"))

    if not workout_exercise_ids:
        return {
            "success": False,
            "error": f"Could not find {exercise_name} in today's workout. Can only edit exercises logged today."
        }

    # Build array with exercise updates - one per workout_exercise_id
    # Only include fields that are being changed
    exercises_to_update = []

    for workout_exercise_id in workout_exercise_ids:
        exercise_update = {
            "workout_exercise_id": workout_exercise_id
        }

        if sets is not None:
            exercise_update["sets"] = sets
        if reps is not None:
            exercise_update["reps"] = reps
        if weight_kg is not None:
            exercise_update["weight_kg"] = weight_kg
        if notes is not None:
            exercise_update["notes"] = notes

        exercises_to_update.append(exercise_update)

    data = {
        "user_id": user_id,
        "exercises": exercises_to_update
    }
    print("edit_workout data:", data)

    return _make_laravel_request("PATCH", "workouts/exercises/edit", data)


# Edit agent - handles corrections to today's logged exercises
edit = Agent(
    name="edit",
    model="gemini-2.5-flash",
    instruction=prompt.EDIT_PROMPT,
    description="Edits workout exercises from today's session",
    tools=[edit_workout]
)
