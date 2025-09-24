import os
from google.adk.agents import Agent
from playwright.async_api import async_playwright

async def fetch_with_playwright(url: str) -> dict:
    """
    Render a page with Playwright Async API and save screenshot in ./images.
    """
    try:
        os.makedirs("images", exist_ok=True)
        screenshot_path = os.path.join("images", "snap.png")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page(user_agent="Mozilla/5.0 (ADK Agent)")
            print(f"Navigating to {url} ...")
            await page.goto(url, wait_until="networkidle")
            print("Page loaded.")
            html = await page.content()
            await page.screenshot(path=screenshot_path, full_page=True)
            await browser.close()

        return {"status": "success", "html": html, "screenshot_path": screenshot_path}
    except Exception as e:
        return {"status": "error", "error": str(e)}

root_agent = Agent(
    name="playwright_fetcher",
    model="gemini-2.0-flash",
    description="Fetches a website using Playwright (async)",
    instruction="Call fetch_with_playwright(url=...) to get HTML and screenshot in ./images.",
    tools=[fetch_with_playwright],
)

