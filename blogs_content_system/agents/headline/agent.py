"""
Headline Specialist Agent
Generates compelling headlines from existing blog content
"""

from google.adk.agents import Agent
from ...schemas import BlogOutput
from .prompt import HEADLINE_AGENT_INSTRUCTIONS

headline_agent = Agent(
    name="headline_specialist",
    model="gemini-2.5-flash",
    description="Generates compelling, conversion-focused headlines from blog content using proven creator frameworks",
    instruction=HEADLINE_AGENT_INSTRUCTIONS,
    output_schema=BlogOutput,
    output_key="blog_output"
)
