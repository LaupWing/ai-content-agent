from google.adk.agents import Agent
from . import prompts
from diet_coach.tools import api_diet_summary_today
    
macro_day_summary_agent = Agent(
    name="macro_day_summary_v1",
    model="gemini-2.5-flash",
    description="Retrieves the daily macro summary for the user.",
    instruction=prompts.MACRO_DAY_SUMMARY_PROMPT,
    tools=[api_diet_summary_today]
)