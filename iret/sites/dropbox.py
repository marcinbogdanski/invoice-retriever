import os
import re
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from playwright.sync_api import sync_playwright

BILLING_URL = "https://www.dropbox.com/manage/billing"
INVOICE_ID_PATTERN = re.compile(r"^dropbox_(\d{4}-\d{2}-\d{2})_([0-9a-f]+)$")
ROW_SELECTOR = ".dig-Table-body [role='row'][data-testid^='billing-history-table-row-']"
TIMEOUT_WAIT_FOR = 15000
MAX_ROWS = 3


def _next_available_path(path: Path) -> Path:
    if not path.exists():
        return path
    counter = 1
    while True:
        candidate = path.with_name(f"{path.stem} ({counter}){path.suffix}")
        if not candidate.exists():
            return candidate
        counter += 1


def _parse_date(raw: str) -> str:
    value = raw.strip()
    for fmt in ("%d/%m/%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(value, fmt).date().isoformat()
        except ValueError:
            continue
    raise AssertionError(f"Unsupported Dropbox date format: {raw}")


def _parse_amount_cents(raw: str) -> int:
    match = re.search(r"([0-9]+(?:\.[0-9]{2})?)", raw.replace(",", ""))
    assert match, f"Unsupported Dropbox amount format: {raw}"
    return int(Decimal(match.group(1)) * 100)


def _parse_currency(raw: str) -> str | None:
    return "USD" if "US$" in raw else None


def _parse_bill_id(invoice_href: str) -> str:
    assert invoice_href, "Dropbox invoice link is missing"
    parsed = urlparse(invoice_href)
    bill_id = parse_qs(parsed.query).get("bill_id", [""])[0]
    assert bill_id, f"Dropbox bill_id was not found in link: {invoice_href}"
    return bill_id


def _absolute_invoice_url(invoice_href: str) -> str:
    if invoice_href.startswith("http://") or invoice_href.startswith("https://"):
        return invoice_href
    assert invoice_href.startswith("/"), f"Unsupported Dropbox invoice link: {invoice_href}"
    return f"https://www.dropbox.com{invoice_href}"


def _collect_records(page) -> list[dict]:
    page.goto(BILLING_URL, wait_until="domcontentloaded")
    page.locator("h2:has-text('Billing history')").first.wait_for(timeout=TIMEOUT_WAIT_FOR)

    rows = page.locator(ROW_SELECTOR)
    row_count = rows.count()
    assert row_count > 0, "No Dropbox billing rows were found"

    records: list[dict] = []
    for row_index in range(min(MAX_ROWS, row_count)):
        row = rows.nth(row_index)
        date = _parse_date(row.locator("[role='cell']").nth(0).inner_text())
        description = row.locator(f"[data-testid='billing-history-table-row-{row_index}-description']").inner_text()
        amount_text = row.locator(f"[data-testid='billing-history-table-row-{row_index}-amount']").inner_text()
        amount_cents = _parse_amount_cents(amount_text)
        currency = _parse_currency(amount_text)

        row.locator("[data-testid='billing-history-more-menu-trigger-button']").click(
            timeout=TIMEOUT_WAIT_FOR
        )
        invoice_link = page.get_by_role("menuitem", name="Invoice").first
        invoice_link.wait_for(timeout=TIMEOUT_WAIT_FOR)
        invoice_href = invoice_link.get_attribute("href") or ""
        bill_id = _parse_bill_id(invoice_href)
        page.keyboard.press("Escape")

        records.append(
            {
                "invoice_id": f"dropbox_{date}_{bill_id}",
                "date": date,
                "description": description,
                "amount_cents": amount_cents,
                "currency": currency,
                "bill_id": bill_id,
                "invoice_href": invoice_href,
            }
        )
    return records


def list_invoices() -> list[dict]:
    cdp_url = os.getenv("CDP_URL", "http://127.0.0.1:9222")
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(cdp_url)
        context = browser.contexts[0] if browser.contexts else browser.new_context()
        page = context.new_page()
        try:
            records = _collect_records(page)
        finally:
            page.close()
    return records


def get_invoice(invoice_id: str, out_dir: Path | None = None) -> Path:
    match = INVOICE_ID_PATTERN.match(invoice_id)
    assert match, f"Invalid invoice id format: {invoice_id}"
    target_date = match.group(1)
    target_bill_id = match.group(2)

    cdp_url = os.getenv("CDP_URL", "http://127.0.0.1:9222")
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(cdp_url)
        context = browser.contexts[0] if browser.contexts else browser.new_context()
        page = context.new_page()
        try:
            records = _collect_records(page)
            record = next(
                r for r in records if r["date"] == target_date and r["bill_id"] == target_bill_id
            )
            page.goto(_absolute_invoice_url(record["invoice_href"]), wait_until="domcontentloaded")
            page.get_by_role("button", name="Print invoice").first.wait_for(timeout=TIMEOUT_WAIT_FOR)

            output_dir = out_dir if out_dir is not None else Path.home() / "Downloads"
            output_dir.mkdir(parents=True, exist_ok=True)
            file_date = record["date"].replace("-", ".")
            file_amount = f"{record['amount_cents'] / 100:.2f}"
            file_amount_with_currency = (
                f"{file_amount} {record['currency']}" if record.get("currency") else file_amount
            )
            output_path = _next_available_path(
                output_dir
                / f"dropbox - {file_date} - {file_amount_with_currency} - {record['bill_id']}.pdf"
            )
            page.pdf(path=str(output_path), print_background=True)
        finally:
            page.close()
    return output_path.resolve()
