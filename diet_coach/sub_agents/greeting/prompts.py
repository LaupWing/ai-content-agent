MACRO_SCANNER_PROMPT = """
The user will include an image. RETURN ONLY STRICT JSON. Do not include any prose.

JSON output format:
{
    "items": [
        {
        "name": "string",
        "grams": number,
        "protein_gram": number,
        "carb_gram": number,
        "fat_gram": number,
        "calories": number,
        "quantity": number
        }
    ],
    "totals": {
        "protein_gram": number,
        "carb_gram": number,
        "fat_gram": number,
        "calories": number
    },
    "confidence": number,
    "notes": "string"
}

Rules:
- Identify visible foods and estimate grams and macros using typical macro density.
- If visibility is poor, explain briefly in "notes" and lower "confidence".
- The entire response must be valid JSON (no markdown fences, no commentary).
"""