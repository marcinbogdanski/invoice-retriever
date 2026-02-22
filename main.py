import sys
from pathlib import Path

INVOICE_DIR = Path(
    "/home/marcin/Dropbox/Business/DroneX_3_Trading/Financial/Invoices2/Obsidian"
)
def main() -> int:
    assert INVOICE_DIR.is_dir(), f"{INVOICE_DIR} is not a directory"

    matches = []
    for path in INVOICE_DIR.rglob("*"):
        if not path.is_file() or path.suffix.lower() != ".pdf":
            continue

        date_value = path.stem.split(" - ")[0]
        matches.append((date_value, path))

    matches.sort(reverse=True)
    for date_value, path in matches:
        print(f"{date_value} | {path}")

    print(f"Found {len(matches)} dated PDF file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
