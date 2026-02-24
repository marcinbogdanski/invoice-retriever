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

## Proxy mode

Start proxy mode on a trusted machine:

```bash
./start-chrome-browser.sh
uv run iret proxy
```

The proxy binds to `0.0.0.0:8765` and exposes:

- `GET /healthz`
- `GET /v1/obsidian/list`
- `GET /v1/obsidian/get/<invoice_id>`

Run commands on a client machine by delegating through proxy:

```bash
IRET_PROXY_URL=http://trusted-host:8765 uv run iret obsidian list
IRET_PROXY_URL=http://trusted-host:8765 uv run iret obsidian get obsidian_2026-02-07_1487-9029
```

## Install (optional)

```bash
cd invoice-retriever
git pull
uv tool install --force .
```
