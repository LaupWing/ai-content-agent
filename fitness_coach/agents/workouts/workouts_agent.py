# agents/workouts/work_agent.py
from google.adk.agents import Agent
from .workout_plan_agent import workout_plan_agent
from .exercise_guide_agent import exercise_guide_agent

workouts_agent = Agent(
    name="workouts_agent",
    model="gemini-2.0-flash",
    description="Workout coach that can return today's plan/full plan or explain exercise steps.",
    instruction=(
        "Decide which specialist to use:\n"
        "- If user asks about today's/tomorrow's/dated plan OR asks for the whole plan/week/month, "
        "  TRANSFER to 'workout_plan'.\n"
        "- If user asks 'how to/steps/form' for an exercise, TRANSFER to 'exercise_guide'.\n"
        "Keep responses short and practical."
    ),
    sub_agents=[workout_plan_agent, exercise_guide_agent],
)
