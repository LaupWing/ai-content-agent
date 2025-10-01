from google.adk.agents import Agent

adjust_meal_agent = Agent(
    name="adjust_meal_v1",
    model="gemini-2.5-flash",
    description="You are an adjust meal agent. Your only TASK is to modify existing meal entries based on user feedback.",
    instruction=prompts.ADJUST_MEAL_PROMPT,
    # output_schema=SavedMealOutput,
    # output_key="macro_scan",
)