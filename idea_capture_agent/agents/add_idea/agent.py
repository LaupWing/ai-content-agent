from google.adk.agents import Agent
from . import prompt
from .tools import create_idea_in_notion

add_idea = Agent(
    name="add_idea",
    model="gemini-2.5-flash",
    instruction=prompt.ADD_IDEA_PROMPT,
    description="Processes raw idea text, generates title/description/tags, and saves to Notion",
    tools=[create_idea_in_notion]
)
