from google.adk.agents import Agent
from google.adk.tools import AgentTool
from .agents.add_idea.agent import add_idea
from . import prompt

root_agent = Agent(
    name="idea_capture",
    model="gemini-2.5-flash",
    instruction=prompt.IDEA_CAPTURE_PROMPT,
    description="You manage ideas in Notion: add, list, query, update, delete, expand, and report.",
    tools=[
        AgentTool(agent=add_idea)
    ]
)
