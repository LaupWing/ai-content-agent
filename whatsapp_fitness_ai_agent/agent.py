# agents/root_agent.py
from __future__ import annotations
from google.adk.tools import AgentTool
from google.adk.agents import Agent
from .sub_agents.workouts_agent.agent import workouts_agent
from .sub_agents.diet_agent.agent import diet_agent

MODEL_GEMINI_2_0_FLASH = "gemini-2.0-flash"

root_agent = Agent(
    name="fitness_coach",
    model=MODEL_GEMINI_2_0_FLASH,
    description="Routes user requests to the correct capability.",
    instruction=(
        "Rules:"
        "Never mention other agents, handoffs, or ‘switching back’. If a question is outside workout tools (e.g., ‘can I work out twice today?’), answer briefly with general, safe guidance instead of transferring"
        "You are the entrypoint. If the user asks anything about workouts "
        "(today’s workout, logging sets, logs, deleting a log, plan/schema), "
        "DELEGATE to the 'workouts' tool. For other topics, respond briefly "
        "with only fitness related questions."
        "DELEGATE to the 'diet' tool for anything diet related "
    ),
    tools=[
        AgentTool(agent=workouts_agent),
        AgentTool(agent=diet_agent),
    ],
)
