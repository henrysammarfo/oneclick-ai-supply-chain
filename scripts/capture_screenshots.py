from pathlib import Path
from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "docs" / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)


def main():
    url = "http://localhost:8000/static/index.html"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.goto(url, wait_until="networkidle")
        page.wait_for_selector("#graph")
        try:
            page.wait_for_selector(".feed-item", timeout=5000)
        except Exception:
            pass
        page.wait_for_timeout(1500)

        page.screenshot(path=str(ASSETS / "ui-overview.png"), full_page=True)

        sidebar = page.locator(".sidebar")
        if sidebar:
            sidebar.screenshot(path=str(ASSETS / "ui-feed.png"))

        browser.close()


if __name__ == "__main__":
    main()
