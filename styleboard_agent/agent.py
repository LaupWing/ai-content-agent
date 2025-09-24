from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from .prompt import STYLEBOARD_PROMPT
from .sub_agents.logo_create.agent import logo_create_agent

root_agent = Agent(
    name="styleboard_creator",
    model="gemini-1.5-flash",  # multimodal; reads the uploaded image
    description="Creates a style seed from an attached image, and can generate a logo via the logo agent.",
    instruction=STYLEBOARD_PROMPT,
    tools=[
        AgentTool(logo_create_agent)
    ],  
)
