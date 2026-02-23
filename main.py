import os
from pathlib import Path
from playwright.sync_api import sync_playwright

# import playwright
# print(playwright.__version__)
# exit(0)

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
        page.wait_for_timeout(1000)

        invoice_section = page.locator("div.setting").filter(
            has_text="Invoices and refunds"
        ).first
        assert invoice_section.count() > 0, "Could not find the Invoices and refunds section"

        view_action = invoice_section.locator("a.button", has_text="View").first
        view_action.first.click(timeout=5000)

        invoice_list = page.locator("div.modal-content div.invoice-list").first
        invoice_list.wait_for(timeout=15000)
        print(f"Invoice view opened. URL: {page.url}")

        invoice_items = page.locator("div.modal-content div.invoice-item")
        invoice_count = invoice_items.count()
        assert invoice_count > 0, "Invoice modal opened but no invoice items found"
        print(f"Found {invoice_count} online invoice row(s).")

        for i in range(invoice_count):
            date_text = invoice_items.nth(i).locator("div.text-muted").first.inner_text().strip()
            print(f"online date: {date_text}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
