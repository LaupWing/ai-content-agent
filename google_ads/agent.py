# file: speed_advice_agent/agent.py
import os, requests
from typing import Dict, Any
from google.adk.agents import Agent

def analyze_page_speed(url: str, strategy: str = "mobile") -> Dict[str, Any]:
    """
    Minimal PageSpeed Insights caller.
    Returns a small, human-friendly payload the agent can turn into advice.
    """
    api_key = os.getenv("PAGESPEED_API_KEY")  # Get one in Google Cloud Console
    api = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
    params = {
        "url": url,
        "key": api_key,
        "strategy": strategy,            # "mobile" (default) or "desktop"
        "category": ["performance","seo"]  # keep it lean
    }
    try:
        r = requests.get(api, params=params, timeout=25)
        r.raise_for_status()
        data = r.json()
        lh = data.get("lighthouseResult", {})
        cats = lh.get("categories", {})
        audits = lh.get("audits", {})

        def val(audit_key, field="numericValue", fallback=None):
            a = audits.get(audit_key, {})
            return a.get(field, fallback)

        # Key metrics (ms / unit-normalized)
        perf_score = int((cats.get("performance", {}).get("score", 0) or 0) * 100)
        lcp_ms = val("largest-contentful-paint", "numericValue")  # milliseconds
        tbt_ms = val("total-blocking-time", "numericValue")
        cls = val("cumulative-layout-shift", "numericValue")

        # Lightweight “opportunities” (top 4)
        opps = []
        for k, a in audits.items():
            if a.get("details", {}).get("type") == "opportunity":
                opps.append({
                    "title": a.get("title"),
                    "estimated_ms": a.get("details", {}).get("overallSavingsMs")
                })
        opps = sorted([o for o in opps if o["estimated_ms"]], key=lambda x: x["estimated_ms"], reverse=True)[:4]

        return {
            "status": "success",
            "url": url,
            "strategy": strategy,
            "score": perf_score,
            "metrics": {
                "lcp_ms": lcp_ms,
                "tbt_ms": tbt_ms,
                "cls": cls,
            },
            "top_opportunities": opps,
        }
    except Exception as e:
        return {"status": "error", "message": f"{type(e).__name__}: {e}"}

root_agent = Agent(
    name="speed_advice_agent",
    model="gemini-2.0-flash",
    description="Takes a URL, runs PageSpeed Insights, and explains simple fixes.",
    instruction=(
        "You receive one input: a URL. Call the tool analyze_page_speed(url). "
        "Then write a short, plain-language report for a non-developer. "
        "Structure your answer as:\n\n"
        "1) One-line verdict with the performance score.\n"
        "2) What this means (brief): explain LCP (loading), TBT (interaction delay), CLS (layout jumps).\n"
        "3) Top fixes (step-by-step, non-technical, bullet list of 5–8 items). "
        "   Use everyday language like 'compress big images' rather than jargon. "
        "   Map metric issues to actions (e.g., High LCP → optimize hero image; High CLS → set fixed sizes for images). "
        "4) Quick checklist with boxes [ ] the user can tick.\n\n"
        "Be concrete and vendor-agnostic. Mention examples (e.g., 'use WebP images', "
        "'enable caching with your hosting panel', 'remove unused apps/plugins'). "
        "If status is error, explain the likely cause (bad URL, blocked by robots, etc.) clearly."
    ),
    tools=[analyze_page_speed],
)
