from google.adk.agents import Agent
from . import prompt

# Researcher agent - gathers information and insights for newsletter content
researcher = Agent(
    name="researcher",
    model="gemini-2.5-flash",
    instruction=prompt.RESEARCHER_PROMPT,
    description="Gathers research, insights, and key points for newsletter topics",
    tools=[]
)
