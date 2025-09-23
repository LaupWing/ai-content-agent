from google.adk.agents import Agent
from google.adk.agents import SequentialAgent
from typing import Dict, Any
from google.adk.tools import ToolContext
import os, requests, json
from . import prompts


SAVE_ENDPOINT = os.getenv("SAVE_ENDPOINT", "http://localhost:8000/api/debug/save_scan")
TIMEOUT = float(os.getenv("API_TIMEOUT_SECONDS", "12.0"))

def save_macro_scan(tool_context: ToolContext, scan_json: str, notes: str = "") -> Dict[str, Any]:
    """
    Persist a macro scan result for the current user.
    AFC-friendly signature: only simple JSON types (str).
    """
    # Parse JSON safely
    try:
        scan = json.loads(scan_json)
    except json.JSONDecodeError:
        # If the model didn't produce valid JSON, store raw
        scan = {"raw": scan_json}

    # If you need the user identity:
    # public_id = tool_context.state.get("public_id")  # ensure you set this in session.state

    # Mocked response (re-enable HTTP when ready)
    # payload = {"public_id": public_id, "scan": scan, "notes": notes}
    # r = requests.post(SAVE_ENDPOINT, json=payload, timeout=TIMEOUT)
    # backend = r.json() if r.headers.get("content-type","").startswith("application/json") else {"status_code": r.status_code, "text": r.text}
    backend = {"status": "mocked"}
    print("--------------------------")
    print("Here is the raw_json", scan)
    print("Here is the backend response", backend)
    print("--------------------------")

    return {"saved": True, "backend_response": backend, "echo": scan}
    
macro_create_record_agent = Agent(
    name="macro_create_record_v1",
    model="gemini-2.0-flash",
    description="Confirms the scanned macro JSON with the user before saving.",
    instruction=prompts.MACRO_SAVE_PROMPT,
    tools=[save_macro_scan],
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