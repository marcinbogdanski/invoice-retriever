from playwright.sync_api import sync_playwright

def main() -> int:
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0] if browser.contexts else browser.new_context()
        page = context.new_page()

        page.goto("https://www.saucedemo.com/", wait_until="domcontentloaded")
        page.wait_for_timeout(1500)  # Let Chrome Password Manager auto-fill
        
        login_button = page.locator("#login-button")
        login_button.click()
        page.wait_for_url("**/inventory.html", timeout=10000)

        item_count = page.locator(".inventory_item").count()
        print(f"Login successful. Inventory items visible: {item_count}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
