"""
Component 2 — Source Register Tool & SHA-256 Hasher
Manages data/sources.csv register.
Computes SHA-256 hashes for files in /sources and appends/updates metadata rows.

Columns:
source_id, title, authority, language, url, retrieved_date, doc_date, sha256
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import sys
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTER_PATH = REPO_ROOT / "data" / "sources.csv"
DEFAULT_SOURCES_DIR = REPO_ROOT / "sources"

COLUMNS = [
    "source_id",
    "title",
    "authority",
    "language",
    "url",
    "retrieved_date",
    "doc_date",
    "sha256",
]


def compute_sha256(file_path: Path) -> str:
    """Compute the SHA-256 checksum of a file on disk."""
    if not file_path.exists() or not file_path.is_file():
        return ""
    h = hashlib.sha256()
    with open(file_path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_register(register_path: Path = DEFAULT_REGISTER_PATH) -> List[Dict[str, str]]:
    """Load existing rows from sources.csv as list of dicts."""
    if not register_path.exists():
        return []
    with open(register_path, "r", newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        return list(reader)


def save_register(rows: List[Dict[str, str]], register_path: Path = DEFAULT_REGISTER_PATH) -> None:
    """Save rows to sources.csv ensuring consistent headers and utf-8 encoding."""
    register_path.parent.mkdir(parents=True, exist_ok=True)
    with open(register_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=COLUMNS)
        writer.writeheader()
        for r in rows:
            # Ensure only standard columns are written
            filtered_row = {col: r.get(col, "") for col in COLUMNS}
            writer.writerow(filtered_row)


def append_or_update_source(
    source_id: str,
    title: str,
    authority: str,
    language: str = "en",
    url: str = "",
    doc_date: str = "",
    retrieved_date: Optional[str] = None,
    file_rel_path: Optional[str] = None,
    register_path: Path = DEFAULT_REGISTER_PATH,
    sources_dir: Path = DEFAULT_SOURCES_DIR,
) -> Dict[str, str]:
    """
    Appends a new source or updates sha256/metadata if source_id already exists.
    Computes sha256 if file is provided in /sources or as an absolute path.
    """
    rows = load_register(register_path)
    existing_idx = None
    for idx, r in enumerate(rows):
        if r.get("source_id") == source_id:
            existing_idx = idx
            break

    # Calculate SHA256 if file is available
    sha256_hash = ""
    if file_rel_path:
        target_file = Path(file_rel_path)
        if not target_file.is_absolute():
            # Check inside sources_dir first, then REPO_ROOT
            candidate = sources_dir / target_file.name
            target_file = candidate if candidate.exists() else (REPO_ROOT / file_rel_path)
        sha256_hash = compute_sha256(target_file)

    row_data = {
        "source_id": source_id,
        "title": title,
        "authority": authority,
        "language": language or "en",
        "url": url or "",
        "retrieved_date": retrieved_date or str(date.today()),
        "doc_date": doc_date or "",
        "sha256": sha256_hash,
    }

    if existing_idx is not None:
        # Keep existing sha256 if newly calculated was empty
        if not row_data["sha256"] and rows[existing_idx].get("sha256"):
            row_data["sha256"] = rows[existing_idx]["sha256"]
        rows[existing_idx] = row_data
    else:
        rows.append(row_data)

    save_register(rows, register_path)
    return row_data


def scan_and_register_sources(
    sources_dir: Path = DEFAULT_SOURCES_DIR,
    register_path: Path = DEFAULT_REGISTER_PATH,
) -> None:
    """
    Helper to populate or update hashes for default placeholder sources in /sources.
    """
    defaults = [
        {
            "source_id": "SRC-WP-BN-1990",
            "title": "Business Names Statute No. 6 of 1990 (Western Province)",
            "authority": "Department of Business Names (Western Province)",
            "language": "en",
            "url": "http://www.wpc.gov.lk",
            "doc_date": "1990-01-01",
            "file": "business_names_statute_1990.txt",
        },
        {
            "source_id": "SRC-MOH-FOOD-1980",
            "title": "Food Control Act No. 26 of 1980",
            "authority": "Ministry of Health",
            "language": "en",
            "url": "http://www.health.gov.lk",
            "doc_date": "1980-01-01",
            "file": "food_control_act_1980.txt",
        },
        {
            "source_id": "SRC-LA-TRADE-1980",
            "title": "Municipal Council Trade Licensing By-Laws",
            "authority": "Colombo Municipal Council",
            "language": "en",
            "url": "https://www.colombo.mc.gov.lk",
            "doc_date": "1980-01-01",
            "file": "cmc_trade_licence_bylaws.txt",
        },
        {
            "source_id": "SRC-NMRA-COSMETICS-2015",
            "title": "National Medicines Regulatory Authority Act No. 5 of 2015",
            "authority": "National Medicines Regulatory Authority (NMRA)",
            "language": "en",
            "url": "https://nmra.gov.lk",
            "doc_date": "2015-07-01",
            "file": "nmra_cosmetics_act_2015.txt",
        },
        {
            "source_id": "SRC-CEA-ENV-2008",
            "title": "National Environmental (Protection and Quality) Regulations No. 1 of 2008",
            "authority": "Central Environmental Authority (CEA)",
            "language": "en",
            "url": "http://www.cea.lk",
            "doc_date": "2008-01-25",
            "file": "cea_environmental_act_2008.txt",
        },
    ]

    for item in defaults:
        append_or_update_source(
            source_id=item["source_id"],
            title=item["title"],
            authority=item["authority"],
            language=item["language"],
            url=item["url"],
            doc_date=item["doc_date"],
            file_rel_path=item["file"],
            register_path=register_path,
            sources_dir=sources_dir,
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Register a legal compliance source and compute sha256.")
    parser.add_argument("--scan", action="store_true", help="Scan and register placeholder sources in /sources")
    parser.add_argument("--source-id", help="Unique source identifier (e.g. SRC-WP-BN-1990)")
    parser.add_argument("--title", help="Title of statute or official publication")
    parser.add_argument("--authority", help="Enforcing or promulgating authority")
    parser.add_argument("--language", default="en", help="Language code (en, si)")
    parser.add_argument("--url", default="", help="Official publication URL")
    parser.add_argument("--doc-date", default="", help="Date of promulgation (YYYY-MM-DD)")
    parser.add_argument("--file", help="Filename or relative path inside /sources")
    parser.add_argument("--register", default=str(DEFAULT_REGISTER_PATH), help="Path to sources.csv")

    args = parser.parse_args()
    reg_path = Path(args.register)

    if args.scan:
        scan_and_register_sources(register_path=reg_path)
        print(f"[OK] Sources registered/updated in {reg_path}")
        return

    if not args.source_id or not args.title or not args.authority:
        print("ERROR: --source-id, --title, and --authority are required unless --scan is used.", file=sys.stderr)
        sys.exit(1)

    result = append_or_update_source(
        source_id=args.source_id,
        title=args.title,
        authority=args.authority,
        language=args.language,
        url=args.url,
        doc_date=args.doc_date,
        file_rel_path=args.file,
        register_path=reg_path,
    )
    print(f"[OK] Successfully registered source: {result['source_id']} (sha256: {result['sha256'][:16]}...)")


if __name__ == "__main__":
    main()
