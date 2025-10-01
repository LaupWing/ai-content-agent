from google.adk.agents import Agent
from google.adk.agents import SequentialAgent
from typing import List, Optional
from pydantic import BaseModel, Field
from .tools import api_diet_add_food_entries, macro_day_summary
import os

from diet_coach.tools import api_diet_summary_today
from . import prompts

API_BASE = os.getenv("SAVE_ENDPOINT", "http://localhost:8001/api")
TIMEOUT = float(os.getenv("API_TIMEOUT_SECONDS", "12.0"))

class MealItem(BaseModel):
    """Single food/drink item detected in the image"""
    name: str = Field(description="Name of the food or drink item")
    quantity: float = Field(description="How many units detected (e.g., 4 for eggs, 250 for ml)")
    unit: str = Field(description="Unit of measurement (e.g., 'eggs', 'grams', 'ml', 'cups', 'slices')")
    estimated_weight_grams: Optional[float] = Field(
        default=None,
        description="Total weight in grams for ALL items of this type (e.g., 4 eggs = 240g total)"
    )
    total_protein_grams: float = Field(
        description="Total protein in grams for ALL items combined (e.g., 4 eggs = 25.2g total, not per egg)"
    )
    total_carbs_grams: float = Field(
        description="Total carbohydrates in grams for ALL items combined"
    )
    total_fat_grams: float = Field(
        description="Total fat in grams for ALL items combined"
    )
    total_calories: float = Field(
        description="Total calories for ALL items combined (e.g., 4 eggs = 360 calories total, not 90)"
    )
    confidence: float = Field(
        ge=0.0, 
        le=1.0,
        description="Confidence score between 0.0 and 1.0"
    )

class MacroScanOutput(BaseModel):
    """Complete meal scan result"""
    items: List[MealItem] = Field(description="List of all food/drink items detected")
    confidence: float = Field(
        ge=0.0,
        le=1.0, 
        description="Overall confidence for the entire scan"
    )
    notes: Optional[str] = Field(
        default=None,
        description="Additional notes about visibility, assumptions, or issues"
    )
    label: Optional[str] = Field(
        default=None,
        description="Optional label or category for this meal"
    )


macro_scanner_agent = Agent(
    name="macro_scanner_v1",
    model="gemini-2.5-flash",
    description="You are a macro scanner agent. Your only TASK is to analyze meal photos and return macro information in strict JSON format.",
    instruction=prompts.MACRO_SCANNER_PROMPT,
    output_schema=MacroScanOutput,
    output_key="macro_scan",
)

macro_save_agent = Agent(
    name="macro_save_v1",
    model="gemini-2.5-flash",
    description="Saves the scanned meal items to the user's diet log.",
    instruction=prompts.MACRO_SAVE_PROMPT,
    tools=[api_diet_add_food_entries],  # wrap in FunctionTool if needed
    output_key="last_saved_meal",
)
    
macro_day_summary_agent = Agent(
    name="macro_day_summary_v1",
    model="gemini-2.5-flash",
    description="Retrieves the daily macro summary for the user.",
    instruction=prompts.MACRO_DAY_SUMMARY_PROMPT,
    tools=[macro_day_summary],  # wrap in FunctionTool if needed
)

macro_scan_pipeline = SequentialAgent(
    name="macro_scan_pipeline",
    description="Step 1: analyze photo → Step 2: save JSON. → Step 3: get meal summary",
    sub_agents=[macro_scanner_agent, macro_save_agent, macro_day_summary_agent],
)