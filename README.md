# Invoice Retriever

Use Playwright to retrieve invoices from selected suppliers.

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

This app relies on Google Password Manager to auto-fill login details.
If a service prompts for login, log in once in this Chrome profile and save credentials.

Run invoice commands in another terminal:

```bash
uv run iret obsidian list
uv run iret obsidian get obsidian_2026-02-07_1487-9029
uv run iret obsidian get obsidian_2026-02-07_1487-9029 --out-dir ~/Downloads
```

`get` saves into `data/obsidian` by default. If the destination file already exists, `iret` fails and does not overwrite it.

## Proxy mode

Start browser on a trusted machine:

```bash
./start-chrome-browser.sh
```

Start proxy mode on a trusted machine:

```bash
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
uv tool install --force --reinstall .
```
