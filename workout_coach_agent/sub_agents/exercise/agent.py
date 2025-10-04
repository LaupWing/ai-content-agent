from typing import Dict
from google.adk import Agent
from . import prompt
from tools import _make_laravel_request

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

exercise = Agent(
    name="exercise",
    model="gemini-2.5-flash",
    instruction=prompt.EXERCISE_PROMPT,
    description="Teaches exercise form, technique, and variations",
    tools=[search_exercises]
)