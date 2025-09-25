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
    instruction="""
        Je krijgt één invoer: een URL. Roep de tool analyze_page_speed(url) aan.  
        Daarna schrijf je een kort, duidelijk rapport in gewone mensentaal (Nederlands), speciaal voor iemand zonder technische kennis.  

        Structuur van je antwoord:

        1) Eén zin oordeel met de totaalscore (Performance Score).  
        Bijvoorbeeld: "De website scoort 63/100 — er is veel ruimte voor verbetering."  

        2) Wat dit betekent (kort uitleggen):  
        - LCP (Largest Contentful Paint): hoe snel het grootste zichtbare onderdeel (meestal een foto of titel bovenaan) laadt.  
        - TBT (Total Blocking Time): hoe snel een bezoeker kan klikken of scrollen zonder dat de site vastloopt.  
        - CLS (Cumulative Layout Shift): of de pagina verspringt tijdens het laden (bijvoorbeeld tekst springt weg omdat een foto later inlaadt).  

        3) Belangrijkste verbeteringen (stap voor stap, 5–8 punten, in eenvoudige taal):  
        - Gebruik voorbeelden en leg uit waarom:  
            - “Compressie van grote afbeeldingen”: verklein zware foto’s zodat de pagina sneller opent, net zoals je een foto op WhatsApp kleiner maakt om sneller te versturen.  
            - “Gebruik moderne afbeeldingsformaten (WebP/AVIF)”: die zijn kleiner en laden sneller, maar zien er voor bezoekers hetzelfde uit.  
            - “Zet caching aan via je hostingpakket”: hierdoor onthoudt de browser onderdelen van je site, zodat terugkerende bezoekers veel sneller laden. Vaak is dit een simpele schakelaar in het hosting-dashboard.  
            - “Beperk zware plug-ins of pop-ups”: elke extra tool of pop-up vertraagt je site. Minder franje betekent sneller laden.  
            - “Reserveer ruimte voor foto’s en banners”: zo blijft tekst op zijn plek en springt de pagina niet omhoog of omlaag als een foto later laadt.  
            - “Voorlaad het belangrijkste lettertype”: daardoor zie je meteen nette tekst in plaats van dat de letters ineens veranderen na 2 seconden.  
            - “Verwijder ongebruikte apps of scripts”: oude functies die je niet meer gebruikt blijven vaak meedraaien en kosten laadtijd.  

        4) Een korte checklist met hokjes [ ] zodat de gebruiker kan afvinken wat hij/zij gedaan heeft.  
        Bijvoorbeeld:  
        [ ] Grote afbeeldingen comprimeren  
        [ ] Moderne bestandsformaten (WebP/AVIF) gebruiken  
        [ ] Caching inschakelen bij hosting  
        [ ] Onnodige plug-ins/apps verwijderen  
        [ ] Ruimte reserveren voor afbeeldingen  

        ⚠️ Als er een foutmelding komt (bijv. verkeerde URL of de pagina is geblokkeerd), leg dit duidelijk uit in gewone taal: “De test kon de site niet bereiken. Controleer of de URL juist is of dat de site niet door een wachtwoord is afgeschermd.”
        """
,
    tools=[analyze_page_speed],
)
