from google.adk.agents import Agent
from .agents.diet.diet_agent import diet_agent
from .agents.workouts.workouts_agent import workouts_agent

root_agent = Agent(
    name="fitness_coach",
    model="gemini-2.0-flash",
    description="Fitness and diet coach that can handle diet (analyze/swaps) and workouts (plans/steps).",
    instruction=(
        "Route intent:\n"
        "- Diet image/analysis/swaps → TRANSFER to 'diet_agent'.\n"
        "- Workout plan (today/full) or exercise steps → TRANSFER to 'workouts_agent'.\n"
        "Keep answers short and actionable. If unsure, ask one clarifying question."
    ),
    sub_agents=[diet_agent, workouts_agent],
)
