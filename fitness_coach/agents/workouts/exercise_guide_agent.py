# agents/workouts/exercise_guide_agent.py
from google.adk.agents import Agent

exercise_guide_agent = Agent(
    name="exercise_guide",
    model="gemini-2.0-flash",
    description="Step-by-step cues/safety for a named exercise (e.g., bench press).",
    instruction=(
        "Provide setup, execution, breathing, common mistakes, and safety tips. Be concise."
    ),
)
