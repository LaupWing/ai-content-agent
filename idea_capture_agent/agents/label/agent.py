from google.adk.agents import Agent
from . import prompt
from .tools import get_existing_tags

label = Agent(
    name="label",
    model="gemini-2.5-flash",
    instruction=prompt.LABEL_PROMPT,
    description="Analyzes idea text and selects appropriate tags, reusing existing tags when possible",
    tools=[get_existing_tags]
)
