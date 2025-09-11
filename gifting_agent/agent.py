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
        "query": prompt,
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
    description="Searches the web and returns product JSON with image, price, vendor.",
    instruction=(
        "When the user asks for gifts/products, CALL the tool 'firecrawl_product_search' with their prompt. "
        "Then RETURN ONLY the strict JSON from the tool in this exact shape:\n"
        "{ 'products': [ { 'product_name': str, 'product_description': str, 'product_url': str, 'product_image': str, 'product_price': str, 'product_vendor': str } ] }\n"
        "No extra text outside the JSON."
    ),
    tools=[firecrawl_product_search],
)
