import os
import requests
from typing import Dict, Any, List
from google.adk.agents import Agent

FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")  # set in your .env

def firecrawl_product_search(prompt: str, limit: int = 10) -> Dict[str, Any]:
    """
    Calls Firecrawl /v2/search with JSON schema to extract product cards.
    Returns: { "products": [ {product_name, product_description, product_url, product_image, product_price, product_vendor} ] }
    """
    if not FIRECRAWL_API_KEY:
        return {"status": "error", "error_message": "Missing FIRECRAWL_API_KEY environment variable"}

    url = "https://api.firecrawl.dev/v2/search"
    print(f"firecrawl_product_search: prompt='{prompt}' limit={limit}")
    # payload = {
    #     "query": prompt,             # <-- dynamic, straight from the agent/user
    #     "sources": ["web"],
    #     "categories": [],
    #     "limit": limit,
    #     "scrapeOptions": {
    #         "onlyMainContent": True,
    #         "includeImages": True,   # helps JSON extraction find images
    #         "formats": [
    #             {
    #                 "type": "json",
    #                 "schema": {
    #                     "type": "object",
    #                     "properties": {
    #                         "product_name":        {"type": "string"},
    #                         "product_description": {"type": "string"},
    #                         "product_url":         {"type": "string"},
    #                         "product_image":       {"type": "string"},
    #                         "product_price":       {"type": "string"},
    #                         "product_vendor":      {"type": "string"}
    #                     },
    #                     "required": ["product_name", "product_url"]
    #                 }
    #             }
    #         ]
    #     }
    # }
    payload = {
        "query": "goku figurine above 1000 dollars",  # <-- dynamic, straight from the agent/user
        "sources": [
            "web",
            "images"
        ],
        "categories": [],
        "limit": 10,
        "scrapeOptions": {
            "onlyMainContent": True,
            "maxAge": 172800000,
            "parsers": [
                "pdf"
            ],
            "formats": [
                {
                    "type": "json",
                    "schema": {
                    "type": "object",
                    "required": [],
                    "properties": {
                        "product_name":        {"type": "string"},
                        "product_description": {"type": "string"},
                        "product_url":         {"type": "string"},
                        "product_image":       {"type": "string"},
                        "product_price":       {"type": "string"},
                        "product_vendor":      {"type": "string"}
                    }
                    }
                }
            ]
        }
    }

    headers = {
        "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        resp = requests.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        return {"status": "error", "error_message": f"firecrawl request failed: {e}"}

    # Firecrawl v2 returns {"success": true, "data": [...] } or {"success": true, "data": {"web":[...]}}
    raw = data.get("data", [])
    if isinstance(raw, dict) and "web" in raw:
        raw = raw["web"]
    print(f"firecrawl_product_search: got {len(raw)} raw results")
    products: List[Dict[str, Any]] = []
    for item in raw:
        # Firecrawl JSON mode attaches your schema extraction on each result (key often named "json")
        extracted = item.get("json") or {}
        if not extracted:
            # fallback: synthesize minimal info from the result itself
            extracted = {
                "product_name": item.get("title", "") or "",
                "product_url": item.get("url", "") or "",
                "product_description": item.get("description", "") or "",
                "product_image": (item.get("images") or [None])[0] or "",
                "product_price": "",
                "product_vendor": ""
            }

        # normalize keys & defaults
        prod = {
            "product_name":        extracted.get("product_name", "") or "",
            "product_description": extracted.get("product_description", "") or "",
            "product_url":         extracted.get("product_url", "") or item.get("url", "") or "",
            "product_image":       extracted.get("product_image", "") or "",
            "product_price":       extracted.get("product_price", "") or "",
            "product_vendor":      extracted.get("product_vendor", "") or ""
        }

        if prod["product_url"] and prod["product_name"]:
            # de-dupe by URL
            if not any(p["product_url"] == prod["product_url"] for p in products):
                products.append(prod)

        if len(products) >= limit:
            break

    return {"status": "success", "products": products}

# ---- Root agent (kept super minimal) ----
root_agent = Agent(
    name="gift_finder_firecrawl",
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
        "- Synthesize a single Firecrawl query string that includes: recipient, occasion, interests/keywords, budget range + currency, delivery constraint, and any store preferences.\n"
        "- CALL the tool 'firecrawl_product_search(prompt=<your synthesized query>, limit=10)'.\n"
        "- Then RETURN ONLY strict JSON in exactly this shape (no prose):\n"
        "{ 'products': [ { 'product_name': str, 'product_description': str, 'product_url': str, 'product_image': str, 'product_price': str, 'product_vendor': str } ] }\n"
        "- Ensure max 10 items. Deduplicate near-identical URLs. If a field is unknown, set it to ''.\n\n"
        "Formatting & Behavior Rules:\n"
        "- During PHASE 1, speak normally (no JSON). Once the tool has been called, output ONLY the JSON.\n"
        "- If user changes constraints after results, repeat PHASE 2 with the updated query.\n"
        "- Avoid speculation on price; prefer values extracted by the tool; leave empty if unclear."
    ),
    tools=[firecrawl_product_search],
)
