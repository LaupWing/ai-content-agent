from typing import Optional, List
from pydantic import BaseModel, Field

class MealItemSaved(BaseModel):
    """A single meal item as stored in the database."""
    id: int = Field(description="Unique ID of this meal item in the database")
    name: str = Field(description="Name of the food item")
    quantity: float = Field(description="Quantity of the item")
    unit: str = Field(description="Unit of measurement, e.g. grams, eggs, ml")
    estimated_weight_grams: Optional[float] = Field(
        default=None,
        description="Total weight in grams for all of this item type"
    )
    total_protein_grams: float = Field(description="Total protein in grams")
    total_carbs_grams: float = Field(description="Total carbohydrates in grams")
    total_fat_grams: float = Field(description="Total fat in grams")
    total_calories: float = Field(description="Total calories for this item")
    confidence: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Confidence score between 0 and 1"
    )


class MealTotals(BaseModel):
    """Total macros for the entire meal."""
    calories: float = Field(description="Total calories of all items combined")
    carbs_grams: float = Field(description="Total carbohydrates in grams")
    fat_grams: float = Field(description="Total fat in grams")
    protein_grams: float = Field(description="Total protein in grams")

class SavedMealOutput(BaseModel):
    """Meal object as returned from the API after saving."""
    id: int = Field(description="Database ID of the meal")
    items: List[MealItemSaved] = Field(description="List of all saved meal items")
    meal_type: Optional[str] = Field(default=None, description="Optional meal type (e.g. breakfast, lunch)")
    notes: Optional[str] = Field(default=None, description="Additional notes provided for the meal")
    source: str = Field(description="Source of the meal entry (e.g., manual, api, import)")
    totals: MealTotals = Field(description="Aggregated macro totals for this meal")
