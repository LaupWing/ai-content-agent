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
    items_json: str,          # JSON string: e.g. '[{"name":"Oatmeal","grams":80,"calories":300}]'
    label: str = "",
    notes: str = "",
    source: str = "manual",
    date: str = "",
) -> Dict[str, Any]:
    """POST /diet/food_entries with whatever items you pass in. No normalization."""
    public_id = tool_context.state.get("public_id")
    if not public_id:
        raise ValueError("Missing public_id in session.state")

    # Just parse to ensure it's a JSON array for the POST body.
    items = json.loads(items_json)  # let it raise if malformed

    payload: Dict[str, Any] = {"public_id": public_id, "items": items}
    if label:  payload["label"]  = label
    if notes:  payload["notes"]  = notes
    if source: payload["source"] = source
    if date:   payload["date"]   = date

    r = requests.post(f"{API_BASE}/diet/food_entries", json=payload, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()
    
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