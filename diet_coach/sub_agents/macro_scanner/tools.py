from typing import Dict, Any
from google.adk.tools import ToolContext
import os, requests, json

API_BASE = os.getenv("SAVE_ENDPOINT", "http://localhost:8001/api")
TIMEOUT = float(os.getenv("API_TIMEOUT_SECONDS", "12.0"))

def api_diet_add_food_entries(
    tool_context: ToolContext,
    macro_scan: Dict[str, Any],
) -> Dict[str, Any]:
    """
    POST /diet/food_entries to add meal items.
    
    Args:
        tool_context: Context containing public_id
        items: JSON array string of items, e.g. 
        notes: Optional notes
        
    Returns:
        API response as dict
        
    Raises:
        ValueError: If public_id is missing
        requests.HTTPError: If API request fails
        json.JSONDecodeError: If items is invalid
    """
    public_id = tool_context.state.get("public_id")
    items = json.dumps(macro_scan.get("items", []))
    notes = macro_scan.get("notes", "")

    if not public_id:
        raise ValueError("Missing public_id in session.state")

    # Parse and validate items JSON
    items = json.loads(items)
    if not isinstance(items, list):
        raise ValueError("items must be a JSON array")
    print(f"Parsed items: {json.dumps(items, indent=2)}")
    # Build payload with only non-empty optional fields
    payload = {
        "public_id": public_id,
        "items": items,
        **{k: v for k, v in {
            "notes": notes,
            "source": "manual",
        }.items() if v}
    }

    fields = ["estimated_weight_grams", "total_protein_grams", "total_carbs_grams", "total_fat_grams", "total_calories"]
    totals = {field: sum(item.get(field, 0) for item in items) for field in fields}
    payload["items"] = items
    payload["totals"] = totals
    
    response = requests.post(
        f"{API_BASE}/diet/food_entries",
        json=payload,
        timeout=TIMEOUT
    )
    response.raise_for_status()
    
    return response.json()

def macro_day_summary(tool_context: ToolContext, macro_scan: Dict[str, Any],) -> str:
    """
    Args:
        tool_context: Context containing public_id
        macro_scan: The macro scan result to summarize
        
    Returns:
        Macro scan summary object as dict
        
    Raises:
        ValueError: If public_id is missing
    """
    items = json.dumps(macro_scan.get("items", []))
    items = json.loads(items)
    notes = macro_scan.get("notes", "")
    public_id = tool_context.state.get("public_id")
    meal = {
        "public_id": public_id,
        "items": items
    }

    fields = ["estimated_weight_grams", "total_protein_grams", "total_carbs_grams", "total_fat_grams", "total_calories"]
    totals = {field: sum(item.get(field, 0) for item in items) for field in fields}
    meal["totals"] = totals
    if notes:
        meal["notes"] = notes


    API_BASE = os.getenv("LARAVEL_API_BASE_URL", "http://localhost:8001/api").rstrip("/")
    day_summary = requests.get(
        f"{API_BASE}/diet/summary/today", 
        params={"public_id": public_id}, 
        timeout=TIMEOUT
    )

    return {
        "meal": meal,
        "day_summary": day_summary.json()
    }
