from google.adk.agents import Agent
from . import prompt

hype = Agent(
    name="hype",
    model="gemini-2.5-flash",
    instruction=prompt.HYPE_PROMPT,
    description="Provides motivation and encouragement to users",
    tools=[]  # No tools needed, pure motivation
)