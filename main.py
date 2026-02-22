import os
import sys

from playwright.sync_api import sync_playwright


def main() -> int:
    cdp_url = os.getenv("CDP_URL", "http://127.0.0.1:9222")
    try:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(cdp_url)
            context = browser.contexts[0] if browser.contexts else browser.new_context()
            page = context.pages[0] if context.pages else context.new_page()
            page.goto("https://example.com", wait_until="domcontentloaded")
            print(f"Connected OK: {page.title()} ({page.url})")
            browser.close()
        return 0
    except Exception as exc:
        print(f"Connection failed to {cdp_url}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
