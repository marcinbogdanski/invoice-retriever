import argparse

from iret.sites import obsidian


def main() -> int:
    parser = argparse.ArgumentParser(prog="iret")
    parser.add_argument("site", choices=["obsidian"])
    parser.add_argument("action", choices=["list", "get"])
    parser.add_argument("invoice_id", nargs="?")
    args = parser.parse_args()

    if args.site == "obsidian" and args.action == "list":
        for record in obsidian.list_invoices():
            print(
                f"{record['invoice_id']} | {record['date']} | "
                f"amount_cents={record['amount_cents']} | {record['description']}"
            )
        return 0

    if args.site == "obsidian" and args.action == "get":
        assert args.invoice_id, "invoice_id is required for get"
        path = obsidian.get_invoice(args.invoice_id)
        print(path)
        return 0

    raise AssertionError("Unsupported command")


if __name__ == "__main__":
    raise SystemExit(main())
