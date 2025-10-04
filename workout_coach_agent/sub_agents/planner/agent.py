from google.adk.agents import Agent
from google.adk.tools import ToolContext
from typing import Dict
from workout_coach_agent.tools import _make_laravel_request
from . import prompt 


def get_active_workout_plan(tool_context: ToolContext = None) -> Dict:
    """
    Gets the user's currently active workout plan.
    
    Args:
        tool_context: Automatically injected by ADK
    
    Returns:
        Dictionary with plan details including name, goal, schedule, and exercises
    
    Example response:
        {
            "has_plan": true,
            "plan": {
                "name": "Push/Pull/Legs 6-Day",
                "goal": "hypertrophy",
                "schedule": {"monday": "push", "tuesday": "pull", ...}
            }
        }
    """
    if tool_context and 'user_id' in tool_context.state:
        user_id = tool_context.state['user_id']
    else:
        return {"error": "User ID not found"}
    
    params = {"user_id": user_id}
    return _make_laravel_request("GET", "workout-plans/active", params)


def get_todays_workout(tool_context: ToolContext = None) -> Dict:
    """
    Gets today's scheduled workout from the user's active plan.
    
    Args:
        tool_context: Automatically injected by ADK
    
    Returns:
        Dictionary with today's exercises, sets, reps, and target weights
    
    Example response:
        {
            "has_workout": true,
            "day": "monday",
            "plan_name": "PPL Split",
            "exercises": [
                {
                    "exercise": {"name": "Bench Press"},
                    "target_sets": 4,
                    "target_reps": "8-10",
                    "target_weight_kg": 60
                }
            ]
        }
    """
    if tool_context and 'user_id' in tool_context.state:
        user_id = tool_context.state['user_id']
    else:
        return {"error": "User ID not found"}
    
    params = {"user_id": user_id}
    return _make_laravel_request("GET", "workout-plans/today", params)

planner = Agent(
    name="planner",
    model="gemini-2.5-flash",
    instruction=prompt.PLANNER_PROMPT,
    description="Prescribes daily workouts based on training programs",
    tools=[get_todays_workout, get_active_workout_plan]
)