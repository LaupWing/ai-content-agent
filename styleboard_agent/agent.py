# pip install google-adk playwright
# playwright install chromium

from google.adk.agents import Agent, run_app

# --- simple Playwright fetcher ---
def fetch_with_playwright(url: str) -> dict:
    """
    Render a page with Playwright (Chromium) and return HTML + screenshot path.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return {"status": "error", "error": "playwright not installed"}

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(user_agent="Mozilla/5.0 (ADK Agent)")
            page.goto(url, wait_until="networkidle", timeout=30000)
            html = page.content()
            screenshot_path = "/tmp/snap.png"
            page.screenshot(path=screenshot_path, full_page=True)
            browser.close()
            return {"status": "success", "html": html, "screenshot_path": screenshot_path}
    except Exception as e:
        return {"status": "error", "error": str(e)}

# --- root agent ---
root_agent = Agent(
    name="playwright_fetcher",
    model="gemini-2.0-flash",
    description="Fetches a website using Playwright",
    instruction="Call fetch_with_playwright(url=...) to get HTML and a screenshot.",
    tools=[fetch_with_playwright],
)

