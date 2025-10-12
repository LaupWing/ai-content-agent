from google.adk.agents import Agent
from . import prompt

# Formatter agent - formats and structures newsletter content
formatter = Agent(
    name="formatter",
    model="gemini-2.5-flash",
    instruction=prompt.FORMATTER_PROMPT,
    description="Formats and structures newsletter content for professional presentation",
    tools=[]
)
