# agents/diet_agent/agent.py
from __future__ import annotations
from google.adk.agents import Agent
from google.adk.tools import AgentTool
from .macro_scanner_agent import macro_scanner_agent

from .tools import (
    api_diet_calories_today,
    api_diet_macros_today,
    api_diet_add_food_entries,
    api_diet_meals_today,
    api_diet_meals,
    api_diet_delete_meal,
)

MODEL = "gemini-2.0-flash"

diet_agent = Agent(
    name="diet",
    model=MODEL,
    description="Handles diet queries: analyze meals, add entries, show calories/macros, list/delete meals.",
    instruction=(
        "You manage diet actions for a fitness app user. "
        "All tools read the user from session.state['public_id'].\n\n"

        "INTENTS → TOOLS:\n"
        " • 'calories today' → api_diet_calories_today()\n"
        " • 'macros today' → api_diet_macros_today()\n"
        " • 'what did I eat today' / 'list meals' → api_diet_meals_today()\n"
        " • 'meals on YYYY-MM-DD' → api_diet_meals(date='YYYY-MM-DD')\n"
        " • Add meal items from text → api_diet_add_food_entries(items=[...], label?, notes?, source='manual')\n"
        " • If the user sends an IMAGE: infer items (name, quantity+unit, calories, protein_g, carbs_g, fat_g, confidence), "
        "   then call api_diet_add_food_entries(items=[...], label?, notes?, source='vision').\n"
        " • 'delete meal 123' → api_diet_delete_meal(meal_id=123)\n\n"
        "If the user sends an IMAGE or asks to estimate from a photo, call macro_scanner_tool first. "

        "RULES:\n"
        " - Macros are grams: protein_g, carbs_g, fat_g. Calories are total kcal per item.\n"
        " - If you can't infer exact portions from an image, ask a brief clarifying question or use reasonable defaults and set lower confidence.\n"
        " - Keep responses short and friendly. Never mention internal tools or other agents."
    ),
    tools=[
        AgentTool(agent = macro_scanner_agent),
        # api_diet_calories_today,
        # api_diet_macros_today,
        # api_diet_add_food_entries,
        # api_diet_meals_today,
        # api_diet_meals,
        # api_diet_delete_meal,
    ],
)
