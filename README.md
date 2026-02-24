# Invoice Retriever

Use Playwright to retrieve invoices form selection of suppliers

## Quick start (fresh clone)

```bash
git clone <repo-url>
cd invoice-retriever
uv sync
```

Start Chrome with remote debugging in one terminal:

```bash
./start-chrome-browser.sh
```

Run invoice commands in another terminal:

```bash
uv run iret obsidian list
uv run iret obsidian get obsidian_2026-02-07_1487-9029
```
