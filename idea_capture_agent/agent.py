from google.adk.agents import Agent
from . import prompt

newsletter_coordinator = Agent(
    name="newsletter_coordinator",
    model="gemini-2.5-flash",
    instruction=prompt.IDEA_CAPTURE_PROMPT,
    description="Main coordinator that handles user requests and routes to newsletter creation pipeline",
    tools=[
        
    ]
)
