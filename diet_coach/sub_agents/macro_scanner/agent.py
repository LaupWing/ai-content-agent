from google.adk.agents import Agent
from google.adk.agents import SequentialAgent
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from google.adk.tools import ToolContext
import os, requests, json
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

def api_diet_add_food_entries(
    tool_context: ToolContext,
    items: str,
    notes: str = "",
) -> Dict[str, Any]:
    """
    POST /diet/food_entries to add meal items.
    
    Args:
        tool_context: Context containing public_id
        items: JSON array string of items, e.g. 
        notes: Optional notes
        
    Returns:
        API response as dict
        
    Raises:
        ValueError: If public_id is missing
        requests.HTTPError: If API request fails
        json.JSONDecodeError: If items is invalid
    """
    public_id = tool_context.state.get("public_id")

    if not public_id:
        raise ValueError("Missing public_id in session.state")

    # Parse and validate items JSON
    items = json.loads(items)
    if not isinstance(items, list):
        raise ValueError("items must be a JSON array")
    print(f"Parsed items: {json.dumps(items, indent=2)}")
    # Build payload with only non-empty optional fields
    payload = {
        "public_id": public_id,
        "items": items,
        **{k: v for k, v in {
            "notes": notes,
            "source": "manual",
        }.items() if v}
    }

    fields = ["estimated_weight_grams", "total_protein_grams", "total_carbs_grams", "total_fat_grams", "total_calories"]
    totals = {field: sum(item.get(field, 0) for item in items) for field in fields}
    payload["items"] = items
    payload["totals"] = totals

    print(f"POST /diet/food_entries: {json.dumps(payload, indent=2)}")
    
    response = requests.post(
        f"{API_BASE}/diet/food_entries",
        json=payload,
        timeout=TIMEOUT
    )
    response.raise_for_status()
    
    return response.json()
    
macro_create_record_agent = Agent(
    name="macro_create_record_v1",
    model="gemini-2.5-flash",
    description="Confirms the scanned macro JSON with the user before saving.",
    instruction=prompts.MACRO_SAVE_PROMPT,
    tools=[api_diet_add_food_entries],  # wrap in FunctionTool if needed
)

macro_scanner_agent = Agent(
    name="macro_scanner_v1",
    model="gemini-2.5-flash",
    description="You are a macro scanner agent. Your only TASK is to analyze meal photos and return macro information in strict JSON format.",
    instruction=prompts.MACRO_SCANNER_PROMPT,
    output_schema=MacroScanOutput,
    output_key="macro_scan",
)


macro_scan_pipeline = SequentialAgent(
    name="macro_scan_pipeline",
    description="Step 1: analyze photo → Step 2: save JSON.",
    sub_agents=[macro_scanner_agent, macro_create_record_agent],
)