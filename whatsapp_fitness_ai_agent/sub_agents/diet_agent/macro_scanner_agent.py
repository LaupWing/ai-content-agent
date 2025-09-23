from google.adk.agents import Agent
from google.adk.agents import SequentialAgent
from typing import Dict, Any
from google.adk.tools import ToolContext
import os, requests, json


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
    
macro_save_agent = Agent(
    name="macro_save_v1",
    model="gemini-2.0-flash",
    description="Saves the previously scanned macro JSON and replies with it.",
    instruction=(
        "You already have the macro JSON in state as {macro_scan}.\n"
        "1) Call save_macro_scan(scan={macro_scan}, notes='vision scan').\n"
        "2) Then reply briefly that it was saved, and PRINT the JSON in a fenced code block.\n"
        "Never mention tools or agents."
    ),
    tools=[save_macro_scan],
)

macro_scanner_agent = Agent(
    name="macro_scanner_v1",
    model="gemini-2.0-flash",
    description="You are a macro scanner agent. Your only TASK is to analyze meal photos and return macro information in strict JSON format.",
    instruction=(
        "The user will include an image. RETURN ONLY STRICT JSON:\n"
        "{items:[{name,grams,protein_g,carb_g,fat_g,kcal}],"
        " totals:{protein_g,carb_g,fat_g,kcal}, confidence:number, notes:string}\n"
        "- Identify visible foods, estimate grams and macros using typical macro density.\n"
        "- If visibility is poor, explain in 'notes' and lower confidence.\n"
        "- Do not output any text outside JSON."
    ),
    output_key="macro_scan",
)


macro_scan_pipeline = SequentialAgent(
    name="macro_scan_pipeline",
    description="Step 1: analyze photo → Step 2: save and show JSON.",
    sub_agents=[macro_scanner_agent, macro_save_agent],
)