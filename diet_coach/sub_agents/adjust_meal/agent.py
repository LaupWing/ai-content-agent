from google.adk.agents import Agent
from . import prompts
from .tools import adjust_meal

adjust_meal_agent = Agent(
    name="adjust_meal_v1",
    model="gemini-2.5-flash",
    description="You are an adjust meal agent. Your only TASK is to modify existing meal entries based on user feedback.",
    instruction=prompts.ADJUST_MEAL_PROMPT,
    tools=[adjust_meal], 
    output_key="adjustment_result"
    # output_schema=SavedMealOutput,
)