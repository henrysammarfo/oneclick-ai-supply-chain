from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "docs" / "submission" / "one_page_report.html"
PDF = ROOT / "docs" / "submission" / "one_page_report.pdf"


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(HTML.as_uri(), wait_until="networkidle")
        page.pdf(path=str(PDF), format="A4", margin={"top": "16mm", "bottom": "16mm", "left": "16mm", "right": "16mm"})
        browser.close()


if __name__ == "__main__":
    main()
