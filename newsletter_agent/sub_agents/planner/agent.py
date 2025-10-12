"""
Planner Agent - Creates table of contents for newsletters
"""
from google.adk.agents import Agent
from . import prompt

planner = Agent(
    name="planner",
    model="gemini-2.5-flash",
    instruction=prompt.PLANNER_PROMPT,
    description="Plans newsletter structure by creating table of contents with sections",
    output_key="sections",  # Store sections array in state
    tools=[]
)
