# agents/macro_scanner/agent.py
from __future__ import annotations
from google.adk.agents import Agent

MODEL = "gemini-2.0-flash"

macro_scanner_agent = Agent(
    name="macro_scanner",
    model=MODEL,
    description="Estimates calories and macros from a single food photo.",
    instruction=(
        "You analyze a SINGLE food photo (optionally with a short text hint) and output ONLY JSON.\n"
        "If no image is provided, ask the user to send a photo (briefly) and STOP.\n\n"
        "OUTPUT STRICTLY AS JSON (no prose), in this schema:\n"
        "{\n"
        '  "items": [\n'
        '    {\n'
        '      "name": "string",\n'
        '      "quantity": number,              // numeric portion amount\n'
        '      "unit": "g|ml|piece|slice|cup|tbsp|tsp",\n'
        '      "calories": number,              // kcal for that quantity\n'
        '      "protein_g": number,\n'
        '      "carbs_g": number,\n'
        '      "fat_g": number,\n'
        '      "confidence": number             // 0..1 for this item\n'
        "    }\n"
        "  ],\n"
        '  "totals": {\n'
        '    "calories": number,\n'
        '    "protein_g": number,\n'
        '    "carbs_g": number,\n'
        '    "fat_g": number\n'
        "  },\n"
        '  "meal_label": "breakfast|lunch|dinner|snack|unknown",\n'
        '  "assumptions": ["string", "..."],\n'
        '  "confidence_overall": number          // 0..1\n'
        "}\n\n"
        "Rules:\n"
        " - Be conservative with portions; state key assumptions.\n"
        " - If multiple visually distinct items exist, list each separately.\n"
        " - If you cannot estimate a macro, still provide a reasonable estimate and reflect uncertainty via lower confidence.\n"
        " - Never mention internal tools or other agents. Output JSON only."
    ),
    sub_agents=[],
)
