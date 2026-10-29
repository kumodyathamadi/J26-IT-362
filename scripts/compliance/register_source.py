"""
Component 2 — Source Register Tool

Usage:
    python scripts/compliance/register_source.py \\
        --source-id SL-CMC-TRADELIC-1980 \\
        --authority "Colombo Municipal Council" \\
        --title "CMC Trade Licence By-Laws 1980" \\
        --doc-type bylaw \\
        --jurisdiction "Colombo Municipal Council" \\
        --language en \\
        --url "" \\
        --effective-date 1980-01-01 \\
        --file data/compliance/raw/cmc_trade_licence_bylaws.pdf

Computes SHA-256 of the file (if it exists), appends a row to
data/compliance/source_register.csv, and rejects duplicates by source_id.
"""

import argparse
import csv
import hashlib
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTER_PATH = REPO_ROOT / "data" / "compliance" / "source_register.csv"

FIELDS = [
    "source_id", "authority", "title", "doc_type", "jurisdiction",
    "language", "url", "retrieved_date", "effective_date",
    "status", "file_path", "sha256",
]


def compute_sha256(path: Path) -> str:
    if not path.exists():
        return ""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_existing_ids() -> set:
    if not REGISTER_PATH.exists():
        return set()
    with open(REGISTER_PATH, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        return {row["source_id"] for row in reader}


def append_row(row: dict) -> None:
    write_header = not REGISTER_PATH.exists()
    REGISTER_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REGISTER_PATH, "a", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        if write_header:
            writer.writeheader()
        writer.writerow(row)


def main() -> None:
    parser = argparse.ArgumentParser(description="Register a compliance source document.")
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--authority", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--doc-type", required=True)
    parser.add_argument("--jurisdiction", required=True)
    parser.add_argument("--language", default="en")
    parser.add_argument("--url", default="")
    parser.add_argument("--effective-date", required=True)
    parser.add_argument("--status", default="active")
    parser.add_argument("--file", default="", help="Path to the raw PDF/document (relative to repo root)")
    args = parser.parse_args()

    existing = load_existing_ids()
    if args.source_id in existing:
        print(f"ERROR: source_id '{args.source_id}' already exists in register. Aborting.", file=sys.stderr)
        sys.exit(1)

    file_path = REPO_ROOT / args.file if args.file else Path("")
    sha = compute_sha256(file_path) if args.file else ""

    row = {
        "source_id": args.source_id,
        "authority": args.authority,
        "title": args.title,
        "doc_type": args.doc_type,
        "jurisdiction": args.jurisdiction,
        "language": args.language,
        "url": args.url,
        "retrieved_date": str(date.today()),
        "effective_date": args.effective_date,
        "status": args.status,
        "file_path": args.file,
        "sha256": sha,
    }
    append_row(row)
    print(f"✓ Registered: {args.source_id}")


if __name__ == "__main__":
    main()
