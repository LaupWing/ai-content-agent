# agents/diet/diet_agent.py
from google.adk.agents import Agent
from .macro_scanner_agent import macro_scanner_agent
from .swaps_agent import swaps_agent

diet_agent = Agent(
    name="diet_agent",
    model="gemini-2.0-flash",
    description="Diet coach that can analyze meal photos OR recommend lower-calorie swaps.",
    instruction=(
        "Decide which specialist to use:\n"
        "- If the user includes an IMAGE or asks to analyze a meal, TRANSFER to 'macro_scanner'.\n"
        "- If the user asks for swaps/alternatives/less calories, TRANSFER to 'food_swaps'.\n"
        "When relevant, pass along the previous macro JSON in context/state."
    ),
    sub_agents=[macro_scanner_agent, swaps_agent]
)
