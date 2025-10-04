from google.adk.agents import Agent
from google.adk.tools import ToolContext
from typing import Dict
from tools import _make_laravel_request
from . import prompt 

def get_workout_history(tool_context: ToolContext, days: int = 7) -> Dict:
    """
    Retrieves the user's recent workout history.
    
    Args:
        tool_context: Context containing user_id
        days: Number of days of history to retrieve (default: 7)
    
    Returns:
        Dictionary containing list of workouts with exercises, dates, and performance data
    
    Example:
        get_workout_history(2, 14)  # Last 2 weeks
    """
    user_id = tool_context.state.get("user_id")
    params = {"user_id": user_id, "days": days}

    return _make_laravel_request("GET", "workouts/history", params)

def get_workout_summary(tool_context: ToolContext, days: int = 7) -> Dict:
    """
    Gets a statistical summary of the user's training.
    
    Args:
        tool_context: Context containing user_id
        days: Number of days to analyze (default: 7)
    
    Returns:
        Dictionary with total workouts, volume, sets, average duration, and exercise list
    
    Example:
        get_workout_summary(2, 30)  # Last month's stats
    """
    user_id = tool_context.state.get("user_id")
    params = {"user_id": user_id, "days": days}
    return _make_laravel_request("GET", "workouts/summary", params)

analyst = Agent(
    name="analyst",
    model="gemini-2.5-flash",
    instruction=prompt.ANALYST_PROMPT,
    description="Analyzes workout data and provides progress insights",
    tools=[get_workout_history, get_workout_summary]
)