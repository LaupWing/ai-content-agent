from google.adk.agents import Agent
from google.adk.tools import AgentTool
from .agents.add_idea.agent import add_idea
from .tools import list_ideas, query_ideas
from . import prompt

root_agent = Agent(
    name="idea_capture",
    model="gemini-2.5-flash",
    instruction=prompt.IDEA_CAPTURE_PROMPT,
    description="Captures and processes raw idea text, generating structured titles, descriptions, and smart tags before saving to Notion. Can also list, query, and filter existing ideas.",
    tools=[
        AgentTool(agent=add_idea),
        list_ideas,
        query_ideas
    ]
)
