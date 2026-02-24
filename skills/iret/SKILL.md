---
name: iret
description: List and download invoices via iret client mode only. Always delegate to a trusted proxy server using IRET_PROXY_URL.
---

# Invoice Retriever CLI

CLI for listing and downloading invoices from supported sites.

Scope: this tool interfaces with supplier sites (vendor billing pages). It is not for accounting software invoice export/download flows.

This system has two parts:

- `iret` client CLI: used by the agent on an untrusted machine
- `iret proxy` server: started by a human on a trusted machine with browser access

## Project

- **Repo:** `https://github.com/marcinbogdanski/invoice-retriever`
- **README:** `https://raw.githubusercontent.com/marcinbogdanski/invoice-retriever/refs/heads/main/README.md`
- **Skill:** `https://raw.githubusercontent.com/marcinbogdanski/invoice-retriever/refs/heads/main/skills/iret/SKILL.md`

## Agent Rules

- Always run in client mode with `IRET_PROXY_URL` set.
- Never run `iret proxy`.
- Never run `./start-chrome-browser.sh`.
- If `IRET_PROXY_URL` is missing or proxy is unreachable, stop and ask user to start/fix proxy.

## Usage (Client Only)

```bash
IRET_PROXY_URL=http://trusted-host:8765 iret obsidian list
IRET_PROXY_URL=http://trusted-host:8765 iret obsidian get <invoice_id>
IRET_PROXY_URL=http://trusted-host:8765 iret obsidian get <invoice_id> --out-dir ~/Downloads
```

The user manages proxy setup. If needed, direct them to README.

## Expected Output

- `list` prints one line per invoice:
  `<invoice_id> | <date> | amount_cents=<amount> | <description>`
- `get` prints the saved local PDF path on success.

## Runtime Notes

- Default output directory is `~/Downloads` unless `--out-dir` is provided.
- If output filename exists, `get` saves as `name (1).pdf`, `name (2).pdf`, etc.

## Proxy API

- `GET /healthz`
- `GET /v1/obsidian/list`
- `GET /v1/obsidian/get/<invoice_id>`
