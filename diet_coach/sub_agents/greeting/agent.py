from __future__ import annotations
from google.adk.agents import Agent
from google.adk.tools import ToolContext
from typing import Dict, Any


MODEL = "gemini-2.0-flash"

def api_diet_has_meals(tool_context: ToolContext) -> Dict[str, Any]:
    """
    Returns {"has_meals": bool, "count": int} by checking if any meals exist.
    Reads session.state['public_id'].
    """
    count = 0;
    # pid = tool_context.state.get("public_id")
    # if not pid:
    #     raise ValueError("Missing public_id in session.state")

    # # Try a lightweight fetch; if your route supports ?limit=1 it’s fast.
    # # Otherwise the controller can ignore `limit`.
    # params = {"public_id": pid, "limit": 1}
    # r = requests.get(f"{API_BASE}/diet/meals", params=params, timeout=TIMEOUT)
    # r.raise_for_status()
    # data = r.json()

    # # Accept either {"meals":[...]} or a plain list response
    # meals = data.get("meals", data if isinstance(data, list) else [])
    # count = len(meals)
    return {"has_meals": count > 0, "count": count}

greeting_agent = Agent(
    name="greeting",
    model=MODEL,
    description="Greets the user and tailors the first message based on whether they’ve logged meals before.",
    instruction=(
        "First, call api_diet_has_meals() to determine if the user is NEW or RETURNING.\n"
        "- If has_meals=false (NEW): Greet warmly and explain the simplest flow:\n"
        "  Ask them to send a food photo; you’ll scan it, estimate calories/macros, and save it automatically. "
        "Keep it to 1–2 short sentences.\n"
        "- If has_meals=true (RETURNING): Greet them back and offer next steps in one sentence: "
        "either send a new meal photo, or ask for 'calories today', 'macros today', or 'what did I eat today'.\n"
        "Never mention internal tools or implementation details. Keep responses casual, friendly, and concise."
    ),
    tools=[api_diet_has_meals],
)