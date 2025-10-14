from google.adk.agents import Agent
from . import prompt

add_idea = Agent(
    name="add_idea",
    model="gemini-2.5-flash",
    instruction=prompt.ADD_IDEA_PROMPT,
    description="",
    tools=[
        
    ]
)
