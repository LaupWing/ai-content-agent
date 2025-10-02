# fitness_coach_adk/fitness_coach/tools.py
"""
Tools for the fitness coach agent to interact with Laravel backend
"""
import httpx
import os
from typing import Dict, List, Optional
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
    user_id: int,
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
    user_id = tool_context.state.get("user_id")
    params = {"user_id": user_id, "days": days}

    return _make_laravel_request("GET", "workouts/history", params)


def get_workout_summary(user_id: int, days: int = 7) -> Dict:
    """
    Gets a statistical summary of the user's training.
    
    Args:
        user_id: The user's database ID
        days: Number of days to analyze (default: 7)
    
    Returns:
        Dictionary with total workouts, volume, sets, average duration, and exercise list
    
    Example:
        get_workout_summary(2, 30)  # Last month's stats
    """
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