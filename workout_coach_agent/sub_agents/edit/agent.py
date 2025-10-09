from google.adk.agents import Agent
from typing import Dict, Optional, List
from google.adk.tools import ToolContext
from . import prompt
from workout_coach_agent.tools import _make_laravel_request


def edit_workout(
    tool_context: ToolContext,
    workout_exercise_ids: List[int],
    sets: Optional[int] = None,
    reps: Optional[int] = None,
    weight_kg: Optional[float] = None,
    notes: Optional[str] = None
) -> Dict:
    """
    Edits workout exercises from today's session by their IDs.

    IMPORTANT: You must first look at tool_context.state['last_workout'] to find the workout_exercise_ids
    for the exercise the user wants to edit. Then pass those IDs to this function.

    Args:
        tool_context: Context containing user_id
        workout_exercise_ids: List of workout_exercise_id values to update (extract from tool_context.state['last_workout'])
        sets: New number of sets (optional, only include if changing)
        reps: New number of reps (optional, only include if changing)
        weight_kg: New weight in kilograms (optional, only include if changing)
        notes: New notes (optional, only include if changing)

    Returns:
        Dictionary with updated exercise details

    Example workflow:
        1. User says: "bench was 120kg not 110kg"
        2. You look at tool_context.state['last_workout']['exercises']
        3. You find all entries where name="Bench Press" and extract their workout_exercise_ids: [22, 23, 24]
        4. You call: edit_workout(tool_context, workout_exercise_ids=[22, 23, 24], weight_kg=120.0)
    """
    user_id = tool_context.state.get("user_id")

    if not workout_exercise_ids:
        return {
            "success": False,
            "error": "No workout_exercise_ids provided. Please extract them from tool_context.state['last_workout']."
        }

    # Build array with exercise updates - one per workout_exercise_id
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

    response = _make_laravel_request("PATCH", "workouts/exercises/edit", data)

    # Update state to keep it in sync with the backend
    if response.get("success"):
        last_workout = tool_context.state.get("last_workout", {})

        if last_workout and "exercises" in last_workout:
            # Update the exercises in state with the new values
            for exercise in last_workout["exercises"]:
                if exercise.get("workout_exercise_id") in workout_exercise_ids:
                    # Update fields that were changed
                    if sets is not None:
                        exercise["set_number"] = sets
                    if reps is not None:
                        exercise["reps"] = reps
                    if weight_kg is not None:
                        exercise["weight_kg"] = weight_kg
                    if notes is not None:
                        exercise["notes"] = notes

            # Update both state keys
            today = last_workout.get("workout_date", "")
            if today:
                date_key = f"last_workout_{today}"
                tool_context.state[date_key] = last_workout

            tool_context.state["last_workout"] = last_workout

    return response


# Edit agent - handles corrections to today's logged exercises
edit = Agent(
    name="edit",
    model="gemini-2.5-flash",
    instruction=prompt.EDIT_PROMPT,
    description="Edits workout exercises from today's session",
    tools=[edit_workout]
)
