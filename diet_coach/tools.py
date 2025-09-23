from __future__ import annotations
from typing import Dict, Any
from google.adk.tools import ToolContext
import os, requests

API_BASE = os.getenv("LARAVEL_API_BASE_URL", "http://localhost:8001/api").rstrip("/")
TIMEOUT  = float(os.getenv("API_TIMEOUT_SECONDS", "12.0"))

def api_diet_macros_today(tool_context: ToolContext) -> Dict[str, Any]:
    """
    Get today's macro totals (calories, protein, carbs, fat) for the current user.
    Reads session.state['public_id'] and calls your Laravel endpoint:
        GET /diet/macros/today?public_id=...
        Returns the backend JSON as-is.
    """
    public_id = tool_context.state.get("public_id")
    if not public_id:
        raise ValueError("Missing public_id in session.state")

    r = requests.get(f"{API_BASE}/diet/macros/today", params={"public_id": public_id}, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()