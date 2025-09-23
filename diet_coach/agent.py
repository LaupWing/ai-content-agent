# agents/root_agent.py
from __future__ import annotations
from google.adk.agents import Agent

MODEL_GEMINI_2_0_FLASH = "gemini-2.0-flash"

root_agent = Agent(
    name="diet_coach",
    model=MODEL_GEMINI_2_0_FLASH,
    description="",
    instruction=(
    ),
    tools=[
    ],
)
