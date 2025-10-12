from google.adk.agents import Agent
from google.adk.tools import GoogleSearchTool
from . import prompt

# Researcher agent - gathers information and insights for newsletter content
# Now with Google Search capability and hyperlink integration
researcher = Agent(
    name="researcher",
    model="gemini-2.5-flash",
    instruction=prompt.RESEARCHER_PROMPT,
    description="Researches individual newsletter sections using Google Search, gathers insights, and provides relevant hyperlinks",
    tools=[GoogleSearchTool()]
)
