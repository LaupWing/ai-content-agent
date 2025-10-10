"""
Polish Agent
Improves existing blog drafts - restructures, enhances, fixes
"""

from google.adk.agents import Agent
from schemas import BlogOutput
from .prompt import POLISH_AGENT_INSTRUCTIONS

polish_agent = Agent(
    name="content_editor",
    model="gemini-2.5-flash",
    description="Expert content editor who polishes blog drafts by improving structure, clarity, and impact while preserving the author's voice and ideas.",
    instruction=POLISH_AGENT_INSTRUCTIONS,
    output_schema=BlogOutput,
    output_key="blog_output"
)
