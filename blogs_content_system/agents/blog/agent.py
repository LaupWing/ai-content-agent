"""
Blog Writer Agent
Writes complete blogs from headlines or topics
"""

from google.adk.agents import Agent
from schemas import BlogOutput
from .prompt import BLOG_WRITER_INSTRUCTIONS

blog_writer_agent = Agent(
    name="blog_writer",
    model="gemini-2.5-flash",
    description="Elite blog writer creating depth-driven content using proven creator frameworks. Writes complete 1500-2500 word blogs from headlines or topics.",
    instruction=BLOG_WRITER_INSTRUCTIONS,
    output_schema=BlogOutput,
    output_key="blog_output"
)
