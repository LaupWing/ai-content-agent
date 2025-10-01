from typing import List, Optional
from pydantic import BaseModel, Field

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