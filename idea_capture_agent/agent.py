from google.adk.agents import Agent
from google.adk.tools import AgentTool
from .agents.add_idea.agent import add_idea
from .agents.expand_idea.agent import expand_idea
from .agents.idea_alchemy.agent import idea_alchemy
from .tools import list_ideas, query_ideas, update_idea, get_random_ideas
from . import prompt

root_agent = Agent(
    name="idea_capture",
    model="gemini-2.5-flash",
    instruction=prompt.IDEA_CAPTURE_PROMPT,
    description="Captures and processes raw idea text, generating structured titles, descriptions, and smart tags before saving to Notion. Can also list, query, update, expand, and filter existing ideas. Features configurable discussion mode for intellectual exploration of ideas.",
    tools=[
        AgentTool(agent=add_idea),
        AgentTool(agent=expand_idea),
        AgentTool(agent=idea_alchemy),
        list_ideas,
        query_ideas,
        update_idea,
        get_random_ideas
    ]
)
