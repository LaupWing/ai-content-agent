"""
Newsletter Agent - Multi-agent system for creating high-quality newsletters
with section-by-section research pipeline and Google Search integration
"""
from google.adk.agents import Agent
from google.adk.tools import AgentTool
from . import prompt
from .sub_agents.planner.agent import planner
from .sub_agents.researcher.agent import researcher
from .sub_agents.writer.agent import writer
from .sub_agents.formatter.agent import formatter


# ═══════════════════════════════════════════════════════════
# ROOT COORDINATOR AGENT
# ═══════════════════════════════════════════════════════════

newsletter_coordinator = Agent(
    name="newsletter_coordinator",
    model="gemini-2.5-flash",
    instruction=prompt.NEWSLETTER_COORDINATOR_PROMPT,
    description="Orchestrates multi-stage pipeline: planner → loop(researcher per section) → writer → formatter",
    tools=[
        AgentTool(agent=planner),
        AgentTool(agent=researcher),
        AgentTool(agent=writer),
        AgentTool(agent=formatter),
    ]
)


# ═══════════════════════════════════════════════════════════
# EXPORT ROOT AGENT (ADK discovers this automatically)
# ═══════════════════════════════════════════════════════════

# This is what ADK api_server will use
root_agent = newsletter_coordinator
