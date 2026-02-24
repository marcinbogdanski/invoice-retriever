import os
import re

from openai import OpenAI
from playwright.sync_api import sync_playwright


def snapshot_for_ai(page) -> str:
    result = page._sync(  # internal Playwright call used by MCP agent flow
        page._impl_obj._channel.send_return_as_dict(
            "snapshotForAI",
            None,
            {"timeout": 10000},
        )
    )
    return result["full"]


def find_tag_with_llm(snapshot: str) -> str:
    client = OpenAI()
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    response = client.responses.create(
        model=model,
        input=[
            {
                "role": "system",
                "content": "Return only one aria-ref tag like e12 or f2e12.",
            },
            {
                "role": "user",
                "content": (
                    "From this Playwright accessibility snapshot, find the tag for the "
                    "\"Add to cart\" button belonging to \"Sauce Labs Bike Light\". "
                    "Return only the tag.\n\n"
                    f"{snapshot}"
                ),
            },
        ],
    )
    # Match aria-ref tags like "e57" (same frame) or "f2e57" (element inside frame 2).
    return re.search(r"(?:f\d+)?e\d+", response.output_text).group(0)


def click_by_tag(page, tag: str) -> None:
    resolved = page._sync(  # internal Playwright call used by MCP agent flow
        page.main_frame._impl_obj._channel.send_return_as_dict(
            "resolveSelector",
            None,
            {"selector": f"aria-ref={tag}"},
        )
    )
    page.locator(resolved["resolvedSelector"]).click()

def main() -> int:
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0] if browser.contexts else browser.new_context()
        page = context.new_page()

        page.goto("https://www.saucedemo.com/", wait_until="domcontentloaded")
        page.wait_for_timeout(1500)  # Let Chrome Password Manager auto-fill
        snapshot = snapshot_for_ai(page)
        print("Snapshot captured.")
        print("=== Snapshot Start ===")
        print(snapshot)
        print("=== Snapshot End ===")
        
        login_button = page.locator("#login-button")
        login_button.click()
        page.wait_for_url("**/inventory.html", timeout=10000)

        snapshot = snapshot_for_ai(page)
        print("Snapshot captured.")
        print("=== Snapshot Start ===")
        print(snapshot)
        print("=== Snapshot End ===")

        tag = find_tag_with_llm(snapshot)
        print(f"LLM returned tag: {tag}")

        click_by_tag(page, tag)
        print("Clicked Add to cart using aria-ref tag.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
