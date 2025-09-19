from google.adk.agents import Agent

MODEL_GEMINI_2_0_FLASH = "gemini-2.0-flash"

root_agent = Agent(
    name="whatsapp_fitness_ai_agent",
    model=MODEL_GEMINI_2_0_FLASH,
    description=(
        ""
    ),
    instruction=(
        ""
    ),
    sub_agents=[],
)
