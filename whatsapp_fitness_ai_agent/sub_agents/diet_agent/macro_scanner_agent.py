from google.adk.agents import Agent
from typing import Dict, Any
from google.adk.tools import ToolContext
import os, requests, json


SAVE_ENDPOINT = os.getenv("SAVE_ENDPOINT", "http://localhost:8000/api/debug/save_scan")
TIMEOUT = float(os.getenv("API_TIMEOUT_SECONDS", "12.0"))

def save_macro_scan(tool_context: ToolContext, scan: Dict[str, Any], notes: str | None = None) -> Dict[str, Any]:
    """Persist a macro scan result for the current user (reads session.state['public_id'])."""
    print("save_macro_scan called with:", scan, notes)
    
    return {"saved": True, "backend_response": {"status": "mocked"}, "echo": scan}
    # public_id = tool_context.state.get("public_id")
    # if not public_id:
    #     raise ValueError("Missing public_id in session.state")

    # payload = {"public_id": public_id, "scan": scan}
    # if notes: payload["notes"] = notes

    # try:
    #     r = requests.post(SAVE_ENDPOINT, json=payload, timeout=TIMEOUT)
    #     try:
    #         backend = r.json()
    #     except Exception:
    #         backend = {"status_code": r.status_code, "text": r.text}
    #     return {"saved": r.ok, "backend_response": backend, "echo": scan}
    # except requests.RequestException as e:
    #     return {"saved": False, "backend_response": {"error": str(e)}, "echo": scan}
    
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

macro_scan_photo_agent = Agent(
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
    tools=[],
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
    tools=[],
)
