# agents/root_agent.py
from __future__ import annotations
from google.adk.agents import Agent
from google.adk.tools import AgentTool, FunctionTool
from .sub_agents.macro_scanner.agent import macro_scan_pipeline
from .tools import api_diet_summary_today
from . import prompt

MODEL_GEMINI_2_0_FLASH = "gemini-2.0-flash"

root_agent = Agent(
    name="diet_agent",
    model=MODEL_GEMINI_2_0_FLASH,
    description=
        "Help users reach weight goals—lose, gain, or maintain—by making food logging effortless. "
        "Analyze meal photos or short texts to estimate calories and macros and log them automatically, "
        "then suggest smarter swaps, portions, and quick recipes, "
        "and surface patterns with simple, motivating recommendations to keep progress on track.",
    instruction=prompt.DIET_COACH_PROMPT,
    tools=[
        AgentTool(agent=macro_scan_pipeline),
        FunctionTool(api_diet_summary_today)
    ],
)

