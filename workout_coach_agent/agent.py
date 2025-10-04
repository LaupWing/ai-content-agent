"""
Workout Coach Agent - Multi-agent system for workout logging and coaching
"""
from google.adk.agents import Agent
from google.adk.tools import AgentTool
from . import prompt
from .sub_agents.hype.agent import hype
from .sub_agents.analysis.agent import analyst
from .sub_agents.logger.agent import logger
from .sub_agents.exercise.agent import exercise
from .sub_agents.planner.agent import planner


# ═══════════════════════════════════════════════════════════
# ROOT COORDINATOR AGENT
# ═══════════════════════════════════════════════════════════

workout_coach = Agent(
    name="workout_coach",
    model="gemini-2.5-flash",
    instruction=prompt.WORKOUT_COACH_PROMPT,
    description="Main workout coaching coordinator that routes to specialist agents",
    tools=[
        AgentTool(agent=logger),
        AgentTool(agent=analyst),
        AgentTool(agent=hype),
        AgentTool(agent=exercise),
        AgentTool(agent=planner),
    ]
)


# ═══════════════════════════════════════════════════════════
# EXPORT ROOT AGENT (ADK discovers this automatically)
# ═══════════════════════════════════════════════════════════

# This is what ADK api_server will use
root_agent = workout_coach