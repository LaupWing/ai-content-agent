from __future__ import annotations
from typing import Dict, Any
from google.adk.tools import ToolContext
import os, requests

API_BASE = os.getenv("LARAVEL_API_BASE_URL", "http://localhost:8001/api").rstrip("/")
TIMEOUT  = float(os.getenv("API_TIMEOUT_SECONDS", "12.0"))

def api_diet_summary_today(tool_context: ToolContext) -> Dict[str, Any]:
    """
    Get today's complete nutrition summary for the current user.
    
    Returns both meals (with items) and macro totals in one call.
    Reads session.state['public_id'] and calls your Laravel endpoint:
        GET /diet/summary/today?public_id=...
    
    Returns:
        {
            "date": "2025-09-26",
            "meals": [...],  # Array of meals with items
            "totals": {
                "calories": 825,
                "protein_grams": 46.3,
                "carbs_grams": 97,
                "fat_grams": 29.3
            },
            "meals_count": 2,
            "items_count": 3
        }
    """
    public_id = tool_context.state.get("public_id")
    if not public_id:
        raise ValueError("Missing public_id in session.state")

    r = requests.get(
        f"{API_BASE}/diet/summary/today", 
        params={"public_id": public_id}, 
        timeout=TIMEOUT
    )
    r.raise_for_status()
    return r.json()
    