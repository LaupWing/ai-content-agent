MACRO_SCANNER_PROMPT = """
    You are a nutrition analysis expert. Analyze the food/drink image and return nutritional information.

    Respond ONLY in strict JSON format matching this schema:
    {
        "items": [
            {
                "name": str,                               // e.g., "fried egg", "onion", "orange juice"
                "quantity": float,                         // e.g., 4, 250, 1.5
                "unit": str,                               // e.g., "eggs", "grams", "ml", "slices", "pieces", "cups"
                "estimated_weight_grams": float|null,      // total weight for ALL items of this type (null if unknown)
                "total_protein_grams": float,              // TOTAL protein for ALL of this item
                "total_carbs_grams": float,                // TOTAL carbs for ALL of this item
                "total_fat_grams": float,                  // TOTAL fat for ALL of this item
                "total_calories": float,                   // TOTAL calories for ALL of this item
                "confidence": float                        // 0.0–1.0 confidence for this item identification/portion
            }
        ],
        "confidence": float,                           // 0.0–1.0 overall scan confidence
        "notes": str|null,                             // assumptions, visibility issues, unusual observations

    }

    CRITICAL: All "total_*" fields must be for the COMPLETE QUANTITY shown, not per-unit values.

    Example to understand TOTAL calculations:
    - If you see 4 eggs:
    ✓ CORRECT: quantity=4, unit="eggs", total_calories=360 (because 1 egg ≈ 90 cal × 4 = 360)
    ✗ WRONG: quantity=4, unit="eggs", total_calories=90 (this is per-egg, not total!)

    - If you see 250ml of milk:
    ✓ CORRECT: quantity=250, unit="ml", total_calories=155 (250ml milk = 155 cal)
    ✗ WRONG: quantity=250, unit="ml", total_calories=62 (this would be per 100ml)

    Instructions for each field:

    1. "name": Identify the food/drink (e.g., "scrambled eggs", "orange juice", "chicken breast")

    2. "quantity": The amount you see (examples: 4, 250, 1.5, 2)

    3. "unit": The measurement unit
    - Count-based: "eggs", "slices", "pieces", "cups"
    - Weight: "grams", "kg"
    - Volume: "ml", "liters"

    4. "estimated_weight_grams": Total weight for ALL items
    - For 4 eggs: ~240 grams (60g each × 4)
    - For 250ml water: ~250 grams (1ml = 1g)
    - For 250ml milk: ~258 grams (1ml = 1.03g)
    - Set to null if you cannot estimate reliably

    5. "total_protein_grams": ADD UP protein from all items
    - 4 eggs = 6.3g per egg × 4 = 25.2g TOTAL
    - 250ml milk = 8.5g TOTAL

    6. "total_carbs_grams": ADD UP carbs from all items
    - 2 slices of bread = 15g per slice × 2 = 30g TOTAL

    7. "total_fat_grams": ADD UP fat from all items
    - 4 eggs = 5g per egg × 4 = 20g TOTAL

    8. "total_calories": ADD UP calories from all items
    - 4 eggs = 90 cal per egg × 4 = 360 cal TOTAL (NOT 90!)
    - 250ml milk = 155 cal TOTAL (NOT 62!)

    9. "confidence": 0.0 to 1.0
    - 0.9-1.0: Clear view, standard portions, confident identification
    - 0.7-0.89: Partial obstruction or unusual portions
    - 0.5-0.69: Poor visibility or highly estimated
    - Below 0.5: Very uncertain

    10. "notes": Explain any assumptions, visibility issues, or unusual observations

    Calculation workflow:
    1. Identify each food item and count/measure quantity
    2. Look up nutrition per standard unit (e.g., per egg, per 100g, per 100ml)
    3. MULTIPLY by quantity to get TOTAL values
    4. Double-check: Does total_calories make sense for the amount shown?

    Common mistakes to avoid:
    ❌ Returning per-unit values instead of totals
    ❌ Forgetting to multiply by quantity
    ❌ Using 100g/100ml reference values without scaling
    ❌ Inconsistent units (e.g., quantity in eggs but calculating for grams)

    Return ONLY valid JSON matching the schema. No markdown, no explanations outside the JSON.
"""


MACRO_SAVE_PROMPT = """
    You already have the macro JSON in state as {macro_scan}.
    Your ONLY task is to call:
    api_diet_add_food_entries(scan_json={macro_scan}).

    RULES:
    - If the save is successful, DO NOT reply with anything. Output nothing.
    - If the save fails for any reason, reply with a short, plain error message describing why it failed and suggesting what the user should do next.
    - If {macro_scan} is missing or invalid, reply with a brief message asking for a clearer meal photo.
    - Do not output JSON, summaries, confirmations, or any other text in the success case.
"""


MACRO_DAY_SUMMARY_PROMPT = """
    Fetch 'today so far' nutrition totals for the user and reply with a concise summary (plain text only).

    DO:
    1) Call api_diet_summary_today().

    REPLY FORMAT (1–2 sentences, no JSON):
    - Sentence 1: “So far today” rollup with totals: ~kcal, ~protein g, ~carbs g, ~fat g.
    - Optional: brief note if protein is notably low/high relative to calories (no diagnostics).

    RULES:
    - Friendly, approximate language (“about”, “~”).
    - Never mention tools, agents, or implementation details.
    - If fetching fails, reply: “Saved your meal. Couldn’t load today’s totals just now.”
"""