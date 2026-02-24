import os
import re
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright

BILLING_URL = "https://obsidian.md/account/billing"
INVOICE_LIST_URL = "https://api.obsidian.md/subscription/invoice/list"
INVOICE_ID_PATTERN = re.compile(r"^obsidian_(\d{4}-\d{2}-\d{2})_(.+)$")
TIMEOUT_LOGIN = 3000
TIMEOUT_WAIT_FOR = 15000

def _to_record(raw: dict) -> dict:
    date = datetime.fromtimestamp(raw["created"] / 1000, tz=timezone.utc).date().isoformat()
    receipt_number = raw.get("receipt_number") or raw.get("id", "")
    return {
        "invoice_id": f"obsidian_{date}_{receipt_number}",
        "date": date,
        "description": raw.get("description", ""),
        "amount_cents": int(raw.get("amount", 0)),
        "receipt_number": receipt_number,
        "charge_id": raw.get("id", ""),
    }


def _open_invoice_list(page, invoices: list) -> None:
    page.goto(BILLING_URL, wait_until="domcontentloaded")
    page.locator("h1:has-text('Sign in to your account'), h2:has-text('Billing')").first.wait_for(
        timeout=TIMEOUT_WAIT_FOR
    )
    if page.get_by_role("heading", name="Sign in to your account").count() > 0:
        page.wait_for_timeout(TIMEOUT_LOGIN)
        page.get_by_role("button", name="Sign in").first.click()
    page.locator("h2:has-text('Billing')").first.wait_for(timeout=TIMEOUT_WAIT_FOR)

    def on_response(response):
        if response.url == INVOICE_LIST_URL:
            invoices.clear()
            invoices.extend(response.json())

    page.on("response", on_response)
    page.locator("div.setting").filter(has_text="Invoices and refunds").first.locator(
        "a.button", has_text="View"
    ).first.click(timeout=TIMEOUT_WAIT_FOR)
    page.locator("div.modal-content div.invoice-list").first.wait_for(timeout=TIMEOUT_WAIT_FOR)
    assert invoices, "Invoice list API response was not captured"


def list_invoices() -> list[dict]:
    cdp_url = os.getenv("CDP_URL", "http://127.0.0.1:9222")
    invoices: list = []
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(cdp_url)
        context = browser.contexts[0] if browser.contexts else browser.new_context()
        page = context.new_page()
        _open_invoice_list(page, invoices)
    return [_to_record(raw) for raw in invoices]


def get_invoice(invoice_id: str, out_dir: Path | None = None) -> Path:
    match = INVOICE_ID_PATTERN.match(invoice_id)
    assert match, f"Invalid invoice id format: {invoice_id}"
    target_date = match.group(1)
    target_receipt_number = match.group(2)

    cdp_url = os.getenv("CDP_URL", "http://127.0.0.1:9222")
    invoices: list = []
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(cdp_url)
        context = browser.contexts[0] if browser.contexts else browser.new_context()
        page = context.new_page()
        _open_invoice_list(page, invoices)
        records = [_to_record(raw) for raw in invoices]
        row_index = next(
            i
            for i, record in enumerate(records)
            if record["date"] == target_date and record["receipt_number"] == target_receipt_number
        )
        record = records[row_index]
        page.locator("div.modal-content div.invoice-item").nth(row_index).locator(
            "button", has_text="View"
        ).first.click(timeout=TIMEOUT_WAIT_FOR)
        page.locator("button", has_text="Print invoice").first.wait_for(timeout=TIMEOUT_WAIT_FOR)
        output_dir = out_dir if out_dir is not None else Path("data/obsidian")
        output_dir.mkdir(parents=True, exist_ok=True)
        file_date = record["date"].replace("-", ".")
        file_amount = f"{record['amount_cents'] / 100:.2f}"
        file_receipt = record["receipt_number"]
        output_path = output_dir / f"dynalist - {file_date} - {file_amount} - {file_receipt}.pdf"
        assert not output_path.exists(), f"File already exists: {output_path}"
        page.pdf(path=str(output_path), print_background=True)
    return output_path.resolve()
