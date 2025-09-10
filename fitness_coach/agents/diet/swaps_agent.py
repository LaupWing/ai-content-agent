# agents/diet/swaps_agent.py
from google.adk.agents import Agent

swaps_agent = Agent(
    name="food_swaps",
    model="gemini-2.0-flash",
    description="Suggest practical food swaps with kcal deltas; can use prior macro JSON.",
    instruction=(
        "If macro JSON is provided, base deltas on it. Return a short bullet list with each swap's "
        "new kcal and Δkcal (negative is fewer), and a one-line summary."
    ),
)
