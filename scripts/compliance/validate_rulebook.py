"""
Component 2 — Rulebook Validator

Validates that:
1. The YAML is parseable and passes the Pydantic ObligationRulebook schema.
2. Every obligation ID is unique.
3. Every evidence source_id exists in source_register.csv.
4. Every non-empty evidence.quote appears verbatim in the processed text
   file for that source_id / page (if the processed file exists).

Usage:
    python scripts/compliance/validate_rulebook.py

Exits with code 0 on success, 1 on any validation failure.
"""

import json
import sys
from pathlib import Path

import yaml

# Adjust path so we can import backend modules
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from backend.app.compliance.schemas import ObligationRulebook  # noqa: E402
from backend.app.compliance.source_registry import _load_register  # noqa: E402

RULEBOOK_PATH = REPO_ROOT / "data" / "compliance" / "rulebook" / "obligations.yaml"
PROCESSED_DIR = REPO_ROOT / "data" / "compliance" / "processed"


def main() -> None:
    errors: list[str] = []

    # 1. Parse YAML
    if not RULEBOOK_PATH.exists():
        print(f"FAIL: rulebook not found at {RULEBOOK_PATH}", file=sys.stderr)
        sys.exit(1)

    with open(RULEBOOK_PATH, encoding="utf-8") as fh:
        raw = yaml.safe_load(fh)

    try:
        rulebook = ObligationRulebook.model_validate(raw)
    except Exception as exc:
        print(f"FAIL: Pydantic validation error: {exc}", file=sys.stderr)
        sys.exit(1)

    # 2. Unique IDs
    seen_ids: set[str] = set()
    for obl in rulebook.obligations:
        if obl.id in seen_ids:
            errors.append(f"Duplicate obligation id: {obl.id}")
        seen_ids.add(obl.id)

    # 3. Every source_id must be in register
    register = _load_register()
    for obl in rulebook.obligations:
        sid = obl.evidence.source_id
        if sid not in register:
            errors.append(f"{obl.id}: evidence source_id '{sid}' not found in source_register.csv")

    # 4. Non-empty quotes must appear verbatim in processed text
    for obl in rulebook.obligations:
        quote = obl.evidence.quote.strip()
        if not quote:
            continue  # draft — skip
        sid = obl.evidence.source_id
        page = obl.evidence.page
        processed_file = PROCESSED_DIR / f"{sid}.json"
        if not processed_file.exists():
            errors.append(
                f"{obl.id}: quote provided but processed file not found: {processed_file}"
            )
            continue
        with open(processed_file, encoding="utf-8") as fh:
            doc = json.load(fh)
        # doc is expected to be a list of {page, text, ...}
        pages = doc if isinstance(doc, list) else doc.get("pages", [])
        if page is not None:
            pages = [p for p in pages if p.get("page") == page]
        full_text = " ".join(p.get("text", "") for p in pages)
        if quote not in full_text:
            errors.append(
                f"{obl.id}: quote not found verbatim in {processed_file} "
                f"(page={page}): '{quote[:80]}...'"
            )

    if errors:
        print("VALIDATION FAILED:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"[OK] Rulebook valid: {len(rulebook.obligations)} obligations, all source IDs verified.")


if __name__ == "__main__":
    main()
