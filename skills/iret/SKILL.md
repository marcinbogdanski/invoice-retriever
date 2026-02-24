---
name: iret
description: List and download invoices via the iret CLI. Supports direct browser automation and proxy delegation. Use when asked to run invoice list/get calls.
---

# Invoice Retriever CLI

CLI wrapper for listing and downloading invoices from supported sites.

## Project

- **Repo:** `https://github.com/marcinbogdanski/invoice-retriever`
- **README:** `https://raw.githubusercontent.com/marcinbogdanski/invoice-retriever/refs/heads/main/README.md`
- **Skill:** `https://raw.githubusercontent.com/marcinbogdanski/invoice-retriever/refs/heads/main/skills/iret/SKILL.md`

## Usage

```bash
iret obsidian list
iret obsidian get <invoice_id>
iret obsidian get <invoice_id> --out-dir ~/Downloads
iret proxy
IRET_PROXY_URL=http://trusted-host:8765 iret obsidian list
IRET_PROXY_URL=http://trusted-host:8765 iret obsidian get <invoice_id>
iret --help
```

## Expected Output

- `list` prints one line per invoice:
  `<invoice_id> | <date> | amount_cents=<amount> | <description>`
- `get` prints the saved local PDF path on success.

## Runtime Notes

- Browser must be started separately with CDP enabled (`./start-chrome-browser.sh`).
- Default CDP URL is `http://127.0.0.1:9222` (override via `CDP_URL`).
- Login is password-manager based; do not enter passwords in automation.
- Fail fast by design:
  - No retries.
  - If output file exists, `get` fails and does not overwrite.

## Proxy API

- `GET /healthz`
- `GET /v1/obsidian/list`
- `GET /v1/obsidian/get/<invoice_id>`
