from google.adk.agents import Agent
from . import prompt

idea_alchemy = Agent(
    name="idea_alchemy",
    model="gemini-2.5-flash",
    instruction=prompt.IDEA_ALCHEMY_PROMPT,
    description="Transforms existing ideas into novel insights through creative combination and synthesis. Takes 2-3 ideas and generates unexpected connections, productive tensions, and unique perspectives."
)
