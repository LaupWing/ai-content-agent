from google.adk.agents import Agent
from . import prompts
    
macro_day_summary_agent = Agent(
    name="macro_day_summary_v1",
    model="gemini-2.5-flash",
    description="Retrieves the daily macro summary for the user.",
    instruction=prompts.MACRO_DAY_SUMMARY_PROMPT,
    # tools=[macro_day_summary],  # wrap in FunctionTool if needed
)