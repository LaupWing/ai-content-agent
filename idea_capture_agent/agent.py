from google.adk.agents import Agent
from . import prompt

idea_capture = Agent(
    name="idea_capture",
    model="gemini-2.5-flash",
    instruction=prompt.IDEA_CAPTURE_PROMPT,
    description="",
    tools=[
        
    ]
)
