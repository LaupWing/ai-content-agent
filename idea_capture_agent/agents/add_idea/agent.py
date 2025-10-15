from google.adk.agents import Agent
from google.adk.tools import get_mcp_tools
from . import prompt

# Get all MCP tools (includes Notion)
mcp_tools = get_mcp_tools()

add_idea = Agent(
    name="add_idea",
    model="gemini-2.5-flash",
    instruction=prompt.ADD_IDEA_PROMPT,
    description="Processes raw idea text, generates title/description/tags, and saves to Notion",
    tools=mcp_tools  # Includes Notion MCP tools
)
