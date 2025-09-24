from google.adk.agents import Agent

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
