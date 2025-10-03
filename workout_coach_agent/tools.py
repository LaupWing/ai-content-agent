# fitness_coach_adk/fitness_coach/tools.py
"""
Tools for the fitness coach agent to interact with Laravel backend
"""
import httpx
import os
from typing import Dict, Optional
from google.adk.tools import ToolContext

# Get Laravel API config from environment
LARAVEL_API_URL = os.getenv("LARAVEL_API_URL", "http://localhost:8001/api")
LARAVEL_API_KEY = os.getenv("LARAVEL_API_KEY", "")

def _make_laravel_request(method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
    """Helper function to make requests to Laravel API"""
    url = f"{LARAVEL_API_URL}/{endpoint}"
    # headers = {"Authorization": f"Bearer {LARAVEL_API_KEY}"}
    headers = {"Authorization": f"Bearer xx"}
    
    try:
        if method == "GET":
            response = httpx.get(url, headers=headers, params=data, timeout=10.0)
            print(f"GET {url} - params: {data} - status: {response.status_code}")
            print(response.url)
        else:
            response = httpx.post(url, headers=headers, json=data, timeout=10.0)
        
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}


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
    print("Fetching workout history...", tool_context.state)
    user_id = tool_context.state.get("user_id")
    print("User ID:", user_id)
    print("------------")
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


def search_exercises(query: str) -> Dict:
    """
    Searches for exercises in the database by name or alias.
    
    Args:
        query: Search term (e.g., "bench", "squat", "pull up")
    
    Returns:
        Dictionary with matching exercises and their details (muscle group, equipment, difficulty)
    
    Example:
        search_exercises("bench")  # Returns bench press variants
    """
    params = {"q": query}
    return _make_laravel_request("GET", "exercises/search", params)



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