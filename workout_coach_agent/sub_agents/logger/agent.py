from google.adk.agents import Agent
from . import prompt 

logger = Agent(
    name="logger",
    model="gemini-2.5-flash",
    instruction=prompt.LOGGER_PROMPT,
    description="Parses natural language and logs workouts to database",
    tools=[log_workout]
)