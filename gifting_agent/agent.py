import os, requests, time, json
from typing import Dict, Any, List
from google.adk.agents import Agent

TIMEOUT = 8

def _extract_image(item: dict) -> str:
    # Prefer cse_image, then og:image, then thumbnails
    pm = item.get("pagemap", {}) or {}
    if isinstance(pm.get("cse_image"), list) and pm["cse_image"]:
        return pm["cse_image"][0].get("src", "") or ""
    if isinstance(pm.get("metatags"), list) and pm["metatags"]:
        img = pm["metatags"][0].get("og:image") or pm["metatags"][0].get("twitter:image")
        if img: return img
    if isinstance(pm.get("cse_thumbnail"), list) and pm["cse_thumbnail"]:
        return pm["cse_thumbnail"][0].get("src", "") or ""
    return ""

def _extract_price(item: dict) -> str:
    # Try JSON-LD product/offer inside pagemap
    pm = item.get("pagemap", {}) or {}
    products = pm.get("product", [])
    if products:
        offers = products[0].get("offers")
        if isinstance(offers, list) and offers:
            return offers[0].get("price") or offers[0].get("pricecurrency") or ""
        if isinstance(offers, dict):
            return offers.get("price") or offers.get("pricecurrency") or ""
    return ""  # leave empty if not present

def product_search_cse(query: str, num: int = 10) -> Dict[str, Any]:
    """
    Search Google CSE and return up to `num` product-like results with image/price when available.
    Env:
      CSE_API_KEY   - your API key
      CSE_OPEN_CX   - your CSE id (open web, or restrict to shopping domains if you prefer)
    """
    KEY = os.getenv("CSE_API_KEY", "")
    CX  = os.getenv("CSE_OPEN_CX", "")
    if not KEY or not CX:
        # Dev fallback
        return {"status": "success", "products": [
            {"title":"Demo Product","url":"https://example.com/p/1","image":"https://example.com/1.jpg","price":""}
        ]}

    out: List[dict] = []
    start = 1
    while len(out) < num and start <= 21:
        r = requests.get(
            "https://www.googleapis.com/customsearch/v1",
            params={"key": KEY, "cx": CX, "q": query, "num": min(10, num-len(out)), "start": start},
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        data = r.json()
        for it in data.get("items", []):
            title = it.get("title","").strip()
            url   = it.get("link","").strip()
            if not url: continue
            image = _extract_image(it)
            price = _extract_price(it)
            out.append({"title": title[:150], "url": url, "image": image, "price": price})
            if len(out) >= num: break
        if not data.get("items"):
            break
        start += 10
        time.sleep(0.2)

    return {"status": "success", "products": out}



root_agent = Agent(
    name="gift_finder_agent",
    model="gemini-2.0-flash",
    description="Finds up to 10 gift products with image and (if available) price.",
    instruction=(
        "When the user asks for gift ideas, call product_search_cse with their prompt. "
        "Return STRICT JSON only:\n"
        "{ 'products': [ { 'title': str, 'url': str, 'image': str, 'price': str } ] }\n"
        "- Ensure image is a direct URL if available; otherwise empty string.\n"
        "- Deduplicate near-identical titles/URLs."
    ),
    tools=[product_search_cse],  # ✅ custom tool (works with sub-agents too, if you add them later)
)