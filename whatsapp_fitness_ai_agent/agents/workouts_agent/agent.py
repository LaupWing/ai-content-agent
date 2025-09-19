# agents/workouts_agent.py
from __future__ import annotations
from google.adk.agents import Agent

from .tools import (
    api_workouts_today,
    api_workouts_schema,
    api_workouts_log_by_id,
    api_workouts_log_by_name,
    api_workouts_logs_today,
    api_workouts_delete_log,
)

MODEL_GEMINI_2_0_FLASH = "gemini-2.0-flash"

workouts_agent = Agent(
    name="workouts",
    model=MODEL_GEMINI_2_0_FLASH,
    description="Handles workout intents: show today's workout, show full schema, log sets, list/delete logs.",
    instruction=(
        "You manage workout actions for a fitness app user chatting via WhatsApp.\n"
        "Supported intents and which tool to call:\n"
        " • 'workout today' → api_workouts_today\n"
        " • 'workout schema/plan' → api_workouts_schema\n"
        " • Log a set by ID → api_workouts_log_by_id(exercise_id, sets, reps, weight, unit)\n"
        " • Log by name when no ID is available → api_workouts_log_by_name(exercise_name, sets, reps, weight, unit)\n"
        " • 'logs today' → api_workouts_logs_today\n"
        " • 'delete log 123' → api_workouts_delete_log(log_id)\n"
        "Rules:\n"
        " - Units: if the user says 'lb/lbs', set unit='lb'. Otherwise default to 'kg'. For bodyweight, use weight=0.\n"
        " - Keep responses short and friendly. Confirm what was logged using the user's stated unit.\n"
        " - If an API returns an error, explain briefly and ask for a correction.\n"
    ),
    tools=[
        api_workouts_today,
        api_workouts_schema,
        api_workouts_log_by_id,
        api_workouts_log_by_name,
        api_workouts_logs_today,
        api_workouts_delete_log,
    ],
)
