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
    description="The main coordinator agent. Handles user requests and delegates workouts/diets to specialists.",
    instruction=(
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
