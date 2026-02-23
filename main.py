import os
from pathlib import Path
from playwright.sync_api import sync_playwright

INVOICE_DIR = Path("/home/marcin/Dropbox/Business/DroneX_3_Trading/Financial/Invoices2/Obsidian")

def main() -> int:
    assert INVOICE_DIR.is_dir(), f"{INVOICE_DIR} is not a directory"

    matches = []
    for path in INVOICE_DIR.rglob("*"):
        if not path.is_file() or path.suffix.lower() != ".pdf":
            continue
        date_value = path.stem.split(" - ")[0]
        matches.append((date_value, path))
    matches.sort(reverse=True)
    print(f"Found {len(matches)} dated PDF file(s).")
    for date_value, path in matches:
        print(f"{date_value} | {path}")

    cdp_url = os.getenv("CDP_URL", "http://127.0.0.1:9222")
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(cdp_url)
        context = browser.contexts[0] if browser.contexts else browser.new_context()
        page = context.pages[0] if context.pages else context.new_page()
        page.goto("https://obsidian.md/account/billing", wait_until="domcontentloaded")
        print(f"Opened: {page.title()} ({page.url})")

        page.locator("h1:has-text('Sign in to your account'), h2:has-text('Billing')").first.wait_for(timeout=5000)

        if page.get_by_role("heading", name="Sign in to your account").count() > 0:
            print("Login page detected")
            page.wait_for_timeout(1000)  # Give Chrome time to auto-fill the login form
            email_input = page.locator("input[type='email']")
            password_input = page.locator("input[type='password']")
            sign_in_button = page.get_by_role("button", name="Sign in")
            assert email_input.count() > 0, "Login page has no email input"
            assert password_input.count() > 0, "Login page has no password input"
            assert sign_in_button.count() > 0, "Login page has no Sign in button"
            sign_in_button.first.click()

        page.locator("h2:has-text('Billing')").first.wait_for(timeout=5000)
        print("Billing page detected")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
