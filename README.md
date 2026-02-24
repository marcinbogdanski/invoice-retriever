# Invoice Retriever

Use Playwright to retrieve invoices from selected suppliers.

Scope: this tool targets supplier/vendor billing sites, not accounting software invoice export flows.

## Project

- **Repo:** `https://github.com/marcinbogdanski/invoice-retriever`
- **README:** `https://raw.githubusercontent.com/marcinbogdanski/invoice-retriever/refs/heads/main/README.md`
- **Skill:** `https://raw.githubusercontent.com/marcinbogdanski/invoice-retriever/refs/heads/main/skills/iret/SKILL.md`

## Operating modes

- `Direct mode` (human): run `iret obsidian ...` on a machine with browser access.
- `Proxy server` (human, trusted machine): run `iret proxy` where authenticated browser/profile is available.
- `Proxy client` (AI agent, untrusted machine): run `IRET_PROXY_URL=... iret obsidian ...` only.

Why proxy exists: it creates a security boundary. Browser cookies, password manager access, and authenticated sessions stay on the trusted machine outside of agent reach; the agent only gets list/get results via API.

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

`get` saves into `~/Downloads` by default. If the filename already exists, `iret` saves as `... (1).pdf`, `... (2).pdf`, and so on.

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
