from google.adk.agents import Agent
from google.adk.agents import SequentialAgent
from .tools import api_diet_add_food_entries, macro_day_summary
from .schemas.MacroScanOutput import MacroScanOutput
import os

from diet_coach.tools import api_diet_summary_today
from . import prompts

API_BASE = os.getenv("SAVE_ENDPOINT", "http://localhost:8001/api")
TIMEOUT = float(os.getenv("API_TIMEOUT_SECONDS", "12.0"))


macro_scanner_agent = Agent(
    name="macro_scanner_v1",
    model="gemini-2.5-flash",
    description="You are a macro scanner agent. Your only TASK is to analyze meal photos and return macro information in strict JSON format.",
    instruction=prompts.MACRO_SCANNER_PROMPT,
    output_schema=MacroScanOutput,
    output_key="macro_scan",
)

macro_save_agent = Agent(
    name="macro_save_v1",
    model="gemini-2.5-flash",
    description="Saves the scanned meal items to the user's diet log.",
    instruction=prompts.MACRO_SAVE_PROMPT,
    tools=[api_diet_add_food_entries],  # wrap in FunctionTool if needed
    output_key="last_saved_meal",
)
    
macro_day_summary_agent = Agent(
    name="macro_day_summary_v1",
    model="gemini-2.5-flash",
    description="Retrieves the daily macro summary for the user.",
    instruction=prompts.MACRO_DAY_SUMMARY_PROMPT,
    tools=[macro_day_summary],  # wrap in FunctionTool if needed
)

macro_scan_pipeline = SequentialAgent(
    name="macro_scan_pipeline",
    description="Step 1: analyze photo → Step 2: save JSON. → Step 3: get meal summary",
    sub_agents=[macro_scanner_agent, macro_save_agent, macro_day_summary_agent],
)