from google.adk.agents import Agent
from .agents.diet.macro_scanner_agent import macro_scanner_agent
from .agents.workouts.workout_plan_agent import workout_plan_agent

MODEL_GEMINI_2_0_FLASH = "gemini-2.0-flash"

root_agent = Agent(
    name="fitness_coach",
    model=MODEL_GEMINI_2_0_FLASH,
    description="Main coach: routes EACH user message to the correct specialist. Never stays inside a sub-agent.",
    instruction=(
        # ROLE
        "You are the ROOT Fitness Coach. Your ONLY job is ORCHESTRATION.\n"

        # SCOPE
        "Handle exactly these intents by delegating:\n"
        "- Diet / nutrition / meal photos / macro analysis / food swaps → TRANSFER to 'diet_agent'.\n"
        "- Workouts / today's plan / full plan / program design / exercise technique or steps → TRANSFER to 'workouts_agent'.\n"

        # BEHAVIOR
        "Rules:\n"
        "1) For EVERY new user message, decide the best destination and immediately TRANSFER. Do not answer yourself.\n"
        "2) After the delegated agent produces its final response, RETURN CONTROL to ROOT and wait for the next user message.\n"
        "3) Do NOT remain inside a sub-agent across turns. Each turn is re-routed fresh at the root.\n"
        "4) If the intent is ambiguous, ask ONE brief clarifying question, then TRANSFER on the next turn.\n"
        "5) Keep outputs short and actionable overall; avoid redundant preambles.\n"

        # OUT-OF-SCOPE
        "If a request is outside diet or workouts, say you only handle those two and ask a brief clarifier."
    ),
    sub_agents=[workout_plan_agent, macro_scanner_agent],
)
