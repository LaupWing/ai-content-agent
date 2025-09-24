# file: ads_qs_agent/agent.py
import os
from typing import Dict, Any, Optional
from google.adk.agents import Agent
from google.ads.googleads.client import GoogleAdsClient

# --- (A) TOOL: fetch QS from Google Ads API ----------------------------------
# Prereqs:
#   pip install google-ads
#   Set GOOGLE_ADS_CONFIGURATION_FILE env var or place google-ads.yaml in CWD.
#   Docs: https://developers.google.com/google-ads/api/docs/client-libs/python
#
# For MVP, we accept a keyword text and look up its criterion stats inside an ad group.
# In production you’d resolve keyword->criterion via a search query first.

def fetch_quality_score(
    customer_id: str,
    ad_group_id: str,
    criterion_id: str,
) -> Dict[str, Any]:
    """
    Returns Quality Score components for a Keyword criterion.
    """
    try:
        client = GoogleAdsClient.load_from_storage(version="v21")
        ga_service = client.get_service("GoogleAdsService")

        query = f"""
          SELECT
            ad_group_criterion.criterion_id,
            ad_group_criterion.keyword.text,
            ad_group_criterion.quality_info.quality_score,
            ad_group_criterion.quality_info.creative_quality_score,
            ad_group_criterion.quality_info.post_click_quality_score,
            ad_group_criterion.quality_info.search_predicted_ctr
          FROM ad_group_criterion
          WHERE
            customer.id = {customer_id}
            AND ad_group.id = {ad_group_id}
            AND ad_group_criterion.criterion_id = {criterion_id}
            AND ad_group_criterion.type = KEYWORD
        """

        results = ga_service.search(customer_id=customer_id, query=query)

        row = next(iter(results), None)
        if not row:
            return {"status": "error", "error_message": "No rows for this criterion."}

        kw = row.ad_group_criterion.keyword.text
        qi = row.ad_group_criterion.quality_info

        # Google Ads returns component statuses; map to readable labels
        def _status(v: Optional[int]) -> str:
            # Values are enums; for MVP just return str(v) or a friendly label.
            return str(v) if v is not None else "UNSPECIFIED"

        payload = {
            "status": "success",
            "keyword": kw,
            "quality_score": getattr(qi, "quality_score", None),
            "ad_relevance": _status(getattr(qi, "creative_quality_score", None)),
            "landing_page_experience": _status(getattr(qi, "post_click_quality_score", None)),
            "expected_ctr": _status(getattr(qi, "search_predicted_ctr", None)),
        }
        return payload

    except Exception as e:
        return {"status": "error", "error_message": f"{type(e).__name__}: {e}"}

# --- (B) The ADK Agent --------------------------------------------------------
root_agent = Agent(
    name="quality_score_watcher",
    model="gemini-2.0-flash",
    description=(
        "Agent that inspects Google Ads Quality Score components and suggests "
        "ad + landing-page copy improvements in Dutch for moving companies."
    ),
    instruction=(
        "Je helpt bij het verbeteren van Google Ads prestaties voor het trefwoord "
        "'verhuisbedrijf'. Gebruik de tool-output om te bepalen welke factor(en) "
        "de Quality Score beperken: expected CTR, ad relevance of landing page "
        "experience. Geef daarna concrete aanbevelingen en genereer beknopte NL-"
        "advertentieteksten (3 varianten) en landingspagina-secties: H1, subkop, "
        "bullet points en primaire CTA. Voeg voorbeeld-URL-slugs per stad toe."
    ),
    tools=[fetch_quality_score],
)
