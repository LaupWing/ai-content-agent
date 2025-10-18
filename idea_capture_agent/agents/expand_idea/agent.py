from google.adk.agents import Agent
from .tools import append_discussion_to_idea
from . import prompt

expand_idea_agent = Agent(
    name="expand_idea",
    model="gemini-2.5-flash",
    instruction=prompt.EXPAND_IDEA_PROMPT,
    description="Intellectual sparring partner that explores ideas through Socratic dialogue, bringing in epistemology, philosophy, and critical thinking frameworks",
    tools=[
        append_discussion_to_idea
    ]
)
