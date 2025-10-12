from google.adk.agents import Agent
from . import prompt

# Writer agent - creates engaging newsletter content
writer = Agent(
    name="writer",
    model="gemini-2.5-flash",
    instruction=prompt.WRITER_PROMPT,
    description="Creates engaging newsletter content tailored to audience and tone",
    tools=[]
)
