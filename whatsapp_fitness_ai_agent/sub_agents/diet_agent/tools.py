# agents/diet_agent/tools.py
from __future__ import annotations
from typing import Dict, Any, List, Optional, TypedDict
from google.adk.tools import ToolContext
import os, requests

API_BASE = os.getenv("LARAVEL_API_BASE_URL", "http://localhost:8000/api").rstrip("/")
TIMEOUT  = float(os.getenv("API_TIMEOUT_SECONDS", "12.0"))

def _pid(ctx: ToolContext) -> str:
    pid = ctx.state.get("public_id")
    if not pid:
        raise ValueError("Missing public_id in session.state. Set it via ADK Web state delta or the API server.")
    return str(pid)

class MealItem(TypedDict, total=False):
    """A single food item with optional macros. All macros are grams."""
    name: str
    quantity: float
    unit: str
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float
    confidence: float

def api_diet_calories_today(tool_context: ToolContext) -> Dict[str, Any]:
    """Return today's total calories for the current user (reads session.state['public_id'])."""
    r = requests.get(f"{API_BASE}/diet/calories/today", params={"public_id": _pid(tool_context)}, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()

def api_diet_macros_today(tool_context: ToolContext) -> Dict[str, Any]:
    """Return today's total macros (kcal, protein_g, carbs_g, fat_g) for the current user."""
    r = requests.get(f"{API_BASE}/diet/macros/today", params={"public_id": _pid(tool_context)}, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()

def api_diet_add_food_entries(
    tool_context: ToolContext,
    items: List[MealItem],
    label: Optional[str] = None,
    notes: Optional[str] = None,
    source: Optional[str] = None,
    date: Optional[str] = None,  # YYYY-MM-DD; if omitted, backend uses "today"
) -> Dict[str, Any]:
    """Create a meal with one or more items.

    Args:
        items: List of food items. Fill whatever fields you can; macros in grams.
        label: Optional meal label, e.g. 'breakfast' | 'lunch' | 'dinner' | 'snack'.
        notes: Optional free text note (e.g. 'from photo').
        source: Optional origin, e.g. 'vision' or 'manual'.
        date: Optional YYYY-MM-DD; if missing, backend uses today.

    Returns:
        dict: {meal_id: int}
    """
    payload = {
        "public_id": _pid(tool_context),
        "items": items,
    }
    if label:  payload["label"]  = label
    if notes:  payload["notes"]  = notes
    if source: payload["source"] = source
    if date:   payload["date"]   = date

    r = requests.post(f"{API_BASE}/diet/food_entries", json=payload, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()

def api_diet_meals_today(tool_context: ToolContext) -> Dict[str, Any]:
    """List today's meals (with items) for the current user."""
    r = requests.get(f"{API_BASE}/diet/meals/today", params={"public_id": _pid(tool_context)}, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()

def api_diet_meals(tool_context: ToolContext, date: str) -> Dict[str, Any]:
    """List meals for a specific date (YYYY-MM-DD)."""
    r = requests.get(f"{API_BASE}/diet/meals", params={"public_id": _pid(tool_context), "date": date}, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()

def api_diet_delete_meal(tool_context: ToolContext, meal_id: int) -> Dict[str, Any]:
    """Delete a meal by ID for the current user."""
    r = requests.delete(f"{API_BASE}/diet/meals/{meal_id}", params={"public_id": _pid(tool_context)}, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()
