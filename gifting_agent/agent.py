import os, json
from pathlib import Path
from typing import Dict, Any, List
from google.adk.agents import Agent

def firecrawl_product_search(_: str = "", limit: int = 10) -> Dict[str, Any]:
    """
    Loads local data.json and returns it as product list.
    The agent will do the reasoning & filtering.
    """
    data_path = Path(__file__).resolve().parent / "data.json"

    if not data_path.exists():
        return {"status": "error", "error_message": f"data.json not found at {data_path}"}

    try:
        with open(data_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except Exception as e:
        return {"status": "error", "error_message": f"Failed to load data.json: {e}"}

    products: List[Dict[str, Any]] = []

    # Accept both flat lists and grouped vendor dictionaries
    if isinstance(raw, list):
        products = raw
    elif isinstance(raw, dict):
        for vendor_key, bucket in raw.items():
            items = (bucket or {}).get("products")
            if isinstance(items, list):
                for it in items:
                    if "product_vendor" not in it or not it["product_vendor"]:
                        it = {**it, "product_vendor": vendor_key}
                    products.append(it)

    # Limit to first N just to avoid overloading context
    return {"status": "success", "products": products[:limit]}


# ---- Root agent (kept super minimal) ----
root_agent = Agent(
    name="gift_finder_catalog",
    model="gemini-2.0-flash",
    description="Conversational gift finder that clarifies requirements, then returns product JSON with image/price/vendor.",
    instruction=(
        "You are a gift concierge. Work in two phases:\n\n"
        "PHASE 1 — Clarify (short Q&A):\n"
        "- Ask up to 4 concise questions to nail the requirements. Prioritize:\n"
        "  1) Recipient & occasion (e.g., sister / birthday)\n"
        "  2) Budget & currency (e.g., €40–€70)\n"
        "  3) Interests/style (anime character, hobbies, brand likes)\n"
        "  4) Delivery constraints (latest delivery date or 'within a week') & region/country\n"
        "  (Optional) Preferred/blocked stores; material/size constraints.\n"
        "- If user says “just search now”, proceed with sensible defaults (currency from user’s region if mentioned; otherwise EUR; delivery ≤7 days).\n"
        "- Keep questions crisp; never ask more than one follow-up at a time.\n\n"
        "PHASE 2 — Search & Return JSON:\n"
        "- CALL the tool 'firecrawl_product_search()' which will load the full catalog from data.json.\n"
        "- From the returned catalog, pick at most 10 products that best match the user's request.\n"
        "- Then RETURN ONLY strict JSON in exactly this shape (no prose):\n"
        "{ 'products': [ { 'product_name': str, 'product_description': str, 'product_url': str, 'product_image': str, 'product_price': str, 'product_vendor': str } ] }\n"
        "- Ensure max 10 items. Deduplicate near-identical URLs. If a field is unknown, set it to ''.\n\n"
        "Formatting & Behavior Rules:\n"
        "- During PHASE 1, speak normally (no JSON). Once the tool has been called, output ONLY the JSON.\n"
        "- If user changes constraints after results, repeat PHASE 2 with the updated query.\n"
        "- Avoid speculation on price; prefer values from the catalog; leave empty if unclear.\n"
        "- If none fit the user’s constraints, output NOTHING (no text)."
    ),
    tools=[firecrawl_product_search],
)
