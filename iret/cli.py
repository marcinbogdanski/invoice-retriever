import argparse
import json
import os
import textwrap
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import quote, unquote, urlparse
from urllib.request import urlopen

PROXY_ENV_VAR = "IRET_PROXY_URL"
PROXY_HOST = "0.0.0.0"
PROXY_PORT = 8765


def _print_records(records: list[dict]) -> None:
    for record in records:
        print(
            f"{record['invoice_id']} | {record['date']} | "
            f"amount_cents={record['amount_cents']} | {record['description']}"
        )


def _local_list(site: str) -> list[dict]:
    if site == "obsidian":
        from iret.sites import obsidian

        return obsidian.list_invoices()
    raise AssertionError(f"Unsupported site: {site}")


def _local_get(site: str, invoice_id: str) -> Path:
    if site == "obsidian":
        from iret.sites import obsidian

        return obsidian.get_invoice(invoice_id)
    raise AssertionError(f"Unsupported site: {site}")


def _proxy_list(base_url: str, site: str) -> list[dict]:
    with urlopen(f"{base_url.rstrip('/')}/v1/{site}/list") as response:
        return json.loads(response.read().decode("utf-8"))


def _proxy_get(base_url: str, site: str, invoice_id: str) -> bytes:
    with urlopen(f"{base_url.rstrip('/')}/v1/{site}/get/{quote(invoice_id, safe='')}") as response:
        return response.read()


def _start_proxy() -> None:
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            path = urlparse(self.path).path

            if path == "/healthz":
                body = b"ok\n"
                self.send_response(200)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return

            if path == "/v1/obsidian/list":
                records = _local_list("obsidian")
                body = json.dumps(records).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return

            if path.startswith("/v1/obsidian/get/"):
                invoice_id = unquote(path[len("/v1/obsidian/get/") :])
                invoice_path = _local_get("obsidian", invoice_id)
                body = invoice_path.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "application/pdf")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return

            self.send_response(404)
            self.end_headers()

    server = HTTPServer((PROXY_HOST, PROXY_PORT), Handler)
    print(f"Proxy is running on http://{PROXY_HOST}:{PROXY_PORT}", flush=True)
    print(
        f"To access proxy run: {PROXY_ENV_VAR}=http://<trusted-host>:{PROXY_PORT} iret obsidian list",
        flush=True,
    )
    server.serve_forever()


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="iret",
        description="Retrieve invoices from supported sites.",
        epilog=textwrap.dedent(
            f"""\
            Examples:
              iret obsidian list
              iret obsidian get obsidian_2026-02-07_1487-9029
              iret proxy

            Delegation:
              Set {PROXY_ENV_VAR}=http://host:{PROXY_PORT} to delegate obsidian list/get via proxy.
            """
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    commands = parser.add_subparsers(dest="command", required=True, metavar="command")

    obsidian_parser = commands.add_parser(
        "obsidian",
        help="Obsidian invoice commands",
        description="Commands for Obsidian invoices.",
    )
    obsidian_commands = obsidian_parser.add_subparsers(
        dest="obsidian_action", required=True, metavar="action"
    )
    obsidian_commands.add_parser("list", help="List invoices")
    get_parser = obsidian_commands.add_parser("get", help="Download invoice PDF")
    get_parser.add_argument("invoice_id", help="Invoice ID, e.g. obsidian_2026-02-07_1487-9029")

    commands.add_parser(
        "proxy",
        help=f"Run proxy server on {PROXY_HOST}:{PROXY_PORT}",
        description=f"Run proxy server on {PROXY_HOST}:{PROXY_PORT}.",
    )
    return parser


def main() -> int:
    legacy_parser = argparse.ArgumentParser(add_help=False)
    legacy_parser.add_argument("--start-proxy", action="store_true", help=argparse.SUPPRESS)
    legacy_args, remaining = legacy_parser.parse_known_args()

    if legacy_args.start_proxy:
        _start_proxy()
        return 0

    parser = _build_parser()
    args = parser.parse_args(remaining)

    if args.command == "proxy":
        _start_proxy()
        return 0

    site = "obsidian"
    action = args.obsidian_action
    proxy_url = os.getenv(PROXY_ENV_VAR)

    if action == "list":
        records = _proxy_list(proxy_url, site) if proxy_url else _local_list(site)
        _print_records(records)
        return 0

    invoice_id = args.invoice_id
    if proxy_url:
        pdf_bytes = _proxy_get(proxy_url, site, invoice_id)
        output_dir = Path(f"data/{site}")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{invoice_id}.pdf"
        output_path.write_bytes(pdf_bytes)
        print(output_path.resolve())
        return 0

    path = _local_get(site, invoice_id)
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
