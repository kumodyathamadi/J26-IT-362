"""
Component 2 — Rulebook Loader & Schema Validator
Loads and strictly validates data/obligations.json against ObligationSchema.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import List, Optional, Union

# Ensure repository root is on sys.path for direct script execution
_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from engine.schema import ObligationSchema, RulebookSchema


class RulebookValidationError(Exception):
    """Raised when obligations.json fails schema or uniqueness validation."""
    pass


def get_default_rulebook_path() -> Path:
    """Resolve default path to data/obligations.json relative to repository root."""
    repo_root = Path(__file__).resolve().parents[1]
    return repo_root / "data" / "obligations.json"


def load_rulebook(path: Optional[Union[str, Path]] = None) -> List[ObligationSchema]:
    """
    Load, parse, and validate obligations from a JSON file.

    Args:
        path: Optional file path. Defaults to data/obligations.json in repo root.

    Returns:
        List of validated ObligationSchema instances.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        RulebookValidationError: If JSON is malformed, schema validation fails,
                                  or duplicate obligation_ids are detected.
    """
    rulebook_path = Path(path) if path is not None else get_default_rulebook_path()

    if not rulebook_path.exists():
        raise FileNotFoundError(f"Rulebook not found at: {rulebook_path}")

    try:
        with open(rulebook_path, "r", encoding="utf-8") as fh:
            raw_data = json.load(fh)
    except json.JSONDecodeError as exc:
        raise RulebookValidationError(f"Invalid JSON format in {rulebook_path}: {exc}") from exc

    # Support both a top-level list [Obligation, ...] or a container {"obligations": [...]}
    if isinstance(raw_data, list):
        items = raw_data
    elif isinstance(raw_data, dict) and "obligations" in raw_data:
        items = raw_data["obligations"]
    else:
        raise RulebookValidationError(
            f"Rulebook in {rulebook_path} must be either a JSON list of obligations or "
            "an object containing an 'obligations' list."
        )

    validated_obligations: List[ObligationSchema] = []
    seen_ids = set()

    for idx, item in enumerate(items):
        try:
            obligation = ObligationSchema.model_validate(item)
        except Exception as exc:
            obl_id = item.get("obligation_id", f"index_{idx}") if isinstance(item, dict) else f"index_{idx}"
            raise RulebookValidationError(
                f"Schema validation error in obligation '{obl_id}' at index {idx}: {exc}"
            ) from exc

        if obligation.obligation_id in seen_ids:
            raise RulebookValidationError(
                f"Duplicate obligation_id detected: '{obligation.obligation_id}'"
            )
        seen_ids.add(obligation.obligation_id)
        validated_obligations.append(obligation)

    return validated_obligations


if __name__ == "__main__":
    import sys

    target_path = Path(sys.argv[1]) if len(sys.argv) > 1 else get_default_rulebook_path()
    try:
        obligations = load_rulebook(target_path)
        print(f"[OK] Rulebook valid! Successfully loaded {len(obligations)} obligations from {target_path}")
        for obl in obligations:
            print(f"  - [{obl.layer.upper()}] {obl.obligation_id}: {obl.title}")
    except Exception as err:
        print(f"[ERROR] Validation failed: {err}", file=sys.stderr)
        sys.exit(1)
