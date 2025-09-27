from google.adk.agents import Agent
from google.adk.agents import SequentialAgent
from typing import Dict, Any
from google.adk.tools import ToolContext
import os, requests, json
from . import prompts


API_BASE = os.getenv("SAVE_ENDPOINT", "http://localhost:8001/api")
TIMEOUT = float(os.getenv("API_TIMEOUT_SECONDS", "12.0"))

def api_diet_add_food_entries(
    tool_context: ToolContext,
    items: str,
    label: str = "",
    notes: str = "",
    source: str = "manual",
    date: str = "",
) -> Dict[str, Any]:
    """
    POST /diet/food_entries to add meal items.
    
    Args:
        tool_context: Context containing public_id
        items: JSON array string of items, e.g. '[{"name":"Oatmeal","grams":80,"calories":300}]'
        label: Optional meal label
        notes: Optional notes
        source: Source type (default: "manual")
        date: Optional date in Y-m-d format
        
    Returns:
        API response as dict
        
    Raises:
        ValueError: If public_id is missing
        requests.HTTPError: If API request fails
        json.JSONDecodeError: If items is invalid
    """
    public_id = tool_context.state.get("public_id")

    if not public_id:
        raise ValueError("Missing public_id in session.state")

    # Parse and validate items JSON
    items = json.loads(items)
    if not isinstance(items, list):
        raise ValueError("items must be a JSON array")
    
    # Build payload with only non-empty optional fields
    payload = {
        "public_id": public_id,
        "items": items,
        **{k: v for k, v in {
            "label": label,
            "notes": notes,
            "source": source,
            "date": date,
        }.items() if v}
    }

    fields = ["total_grams", "total_protein_gram", "total_carb_gram", "total_fat_gram", "total_calories"]
    totals = {field: sum(item.get(field, 0) for item in items) for field in fields}
    payload["items"] = items
    payload["totals"] = totals

    print(f"POST /diet/food_entries: {json.dumps(payload, indent=2)}")
    
    response = requests.post(
        f"{API_BASE}/diet/food_entries",
        json=payload,
        timeout=TIMEOUT
    )
    response.raise_for_status()
    
    return response.json()
    
macro_create_record_agent = Agent(
    name="macro_create_record_v1",
    model="gemini-2.0-flash",
    description="Confirms the scanned macro JSON with the user before saving.",
    instruction=prompts.MACRO_SAVE_PROMPT,
    tools=[api_diet_add_food_entries],  # wrap in FunctionTool if needed
)

macro_scanner_agent = Agent(
    name="macro_scanner_v1",
    model="gemini-2.0-flash",
    description="You are a macro scanner agent. Your only TASK is to analyze meal photos and return macro information in strict JSON format.",
    instruction=prompts.MACRO_SCANNER_PROMPT,
    output_key="macro_scan",
)


macro_scan_pipeline = SequentialAgent(
    name="macro_scan_pipeline",
    description="Step 1: analyze photo → Step 2: save JSON.",
    sub_agents=[macro_scanner_agent, macro_create_record_agent],
)