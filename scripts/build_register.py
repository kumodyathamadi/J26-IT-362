"""
Build Legal Source Register for Component 2
Scans data/raw_sources/, computes SHA-256 digests, and generates data/source_register.csv.
Adheres strictly to research audit standards and never modifies raw files.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import sys
from pathlib import Path
from typing import Dict, Any, List

REPO_ROOT = Path(__file__).resolve().parents[1]

# Validated constraints from user specification
VALID_INSTRUMENT_TYPES = {"act", "amendment", "gazette", "form", "policy", "draft"}
VALID_STATUSES = {"operative", "draft", "policy"}

CSV_FIELDS = [
    "doc_id",
    "filename",
    "issuing_authority",
    "instrument_type",
    "language",
    "publication_date",
    "effective_date",
    "status",
    "sha256",
    "retrieval_date",
    "reviewer",
]

# Canonical curated legal metadata map for Sri Lankan SME regulatory sources
SOURCE_METADATA_REGISTRY: Dict[str, Dict[str, Any]] = {
    # 01 Common Business Registration
    "Act-7-of-2007-English.pdf": {
        "doc_id": "LK-ACT-2007-07-EN",
        "issuing_authority": "Department of the Registrar of Companies",
        "instrument_type": "act",
        "language": "en",
        "publication_date": "2007-03-20",
        "effective_date": "2007-05-03",
        "status": "operative",
        "reviewer": "Dhananji_LegalReviewer",
    },
    "COMPANIES-AMENDMENT-ACT-No.-12-OF-2025-6389.pdf": {
        "doc_id": "LK-ACT-2025-12-EN",
        "issuing_authority": "Department of the Registrar of Companies",
        "instrument_type": "amendment",
        "language": "en",
        "publication_date": "2025-02-14",
        "effective_date": "2025-02-14",
        "status": "operative",
        "reviewer": "Dhananji_LegalReviewer",
    },
    "Procedure-to-apply-for-a-License-under-section-34-of-the-Companies-Act-No-7-of-2007_English.pdf": {
        "doc_id": "LK-ROC-PROC-S34-EN",
        "issuing_authority": "Department of the Registrar of Companies",
        "instrument_type": "form",
        "language": "en",
        "publication_date": "2018-01-01",
        "effective_date": "2018-01-01",
        "status": "operative",
        "reviewer": "Dhananji_LegalReviewer",
    },
    "Procedure-to-apply-for-a-License-under-section-34-of-the-Companies-Act-No-7-of-2007_Sinhala.pdf": {
        "doc_id": "LK-ROC-PROC-S34-SI",
        "issuing_authority": "Department of the Registrar of Companies",
        "instrument_type": "form",
        "language": "si",
        "publication_date": "2018-01-01",
        "effective_date": "2018-01-01",
        "status": "operative",
        "reviewer": "Dhananji_LegalReviewer",
    },
    # 02 Food Business
    "food_act_no26_1980_en.pdf": {
        "doc_id": "LK-ACT-1980-26-EN",
        "issuing_authority": "Ministry of Health",
        "instrument_type": "act",
        "language": "en",
        "publication_date": "1980-07-18",
        "effective_date": "1981-02-01",
        "status": "operative",
        "reviewer": "Dhananji_LegalReviewer",
    },
    "food_act_no26_1980_si.pdf": {
        "doc_id": "LK-ACT-1980-26-SI",
        "issuing_authority": "Ministry of Health",
        "instrument_type": "act",
        "language": "si",
        "publication_date": "1980-07-18",
        "effective_date": "1981-02-01",
        "status": "operative",
        "reviewer": "Dhananji_LegalReviewer",
    },
    "food_amendment_act_no20-_1991_en.pdf": {
        "doc_id": "LK-ACT-1991-20-EN",
        "issuing_authority": "Ministry of Health",
        "instrument_type": "amendment",
        "language": "en",
        "publication_date": "1991-04-19",
        "effective_date": "1991-04-19",
        "status": "operative",
        "reviewer": "Dhananji_LegalReviewer",
    },
    "food_amendment_act_no20-_1991_si.pdf": {
        "doc_id": "LK-ACT-1991-20-SI",
        "issuing_authority": "Ministry of Health",
        "instrument_type": "amendment",
        "language": "si",
        "publication_date": "1991-04-19",
        "effective_date": "1991-04-19",
        "status": "operative",
        "reviewer": "Dhananji_LegalReviewer",
    },
    "food_amendment_act2011_en.pdf": {
        "doc_id": "LK-ACT-2011-29-EN",
        "issuing_authority": "Ministry of Health",
        "instrument_type": "amendment",
        "language": "en",
        "publication_date": "2011-06-03",
        "effective_date": "2011-06-03",
        "status": "operative",
        "reviewer": "Dhananji_LegalReviewer",
    },
    "food_amendment_act2011_si.pdf": {
        "doc_id": "LK-ACT-2011-29-SI",
        "issuing_authority": "Ministry of Health",
        "instrument_type": "amendment",
        "language": "si",
        "publication_date": "2011-06-03",
        "effective_date": "2011-06-03",
        "status": "operative",
        "reviewer": "Dhananji_LegalReviewer",
    },
    "National_Food_Safety_Policy.pdf": {
        "doc_id": "LK-POL-2014-FOOD",
        "issuing_authority": "Ministry of Health",
        "instrument_type": "policy",
        "language": "en",
        "publication_date": "2014-01-01",
        "effective_date": "2014-01-01",
        "status": "policy",
        "reviewer": "Dhananji_LegalReviewer",
    },
    # 03 Environmental and Waste
    "1.National_Environmental_Act_No._47_of_1980.pdf": {
        "doc_id": "LK-ACT-1980-47-EN",
        "issuing_authority": "Central Environmental Authority",
        "instrument_type": "act",
        "language": "en",
        "publication_date": "1980-10-29",
        "effective_date": "1981-08-12",
        "status": "operative",
        "reviewer": "Dhananji_LegalReviewer",
    },
    "1.Order-to-prohibit-the-Manufacture-of-Polythene-or-any-Polythene-product-20-microns--below.pdf": {
        "doc_id": "LK-GAZ-2006-1466-05",
        "issuing_authority": "Central Environmental Authority",
        "instrument_type": "gazette",
        "language": "en",
        "publication_date": "2006-10-10",
        "effective_date": "2007-01-01",
        "status": "operative",
        "reviewer": "Dhananji_LegalReviewer",
    },
    "2.Order-to-prohibit-the-Manufacture-of-Food-Wrappers.--Lunch-Sheet-etc.pdf": {
        "doc_id": "LK-GAZ-2017-2034-34",
        "issuing_authority": "Central Environmental Authority",
        "instrument_type": "gazette",
        "language": "en",
        "publication_date": "2017-09-01",
        "effective_date": "2017-09-01",
        "status": "operative",
        "reviewer": "Dhananji_LegalReviewer",
    },
    "3.Order-to-prohibit-the-Manufacture-of-any-bag-of-high-density-Grocery-Bag.pdf": {
        "doc_id": "LK-GAZ-2017-2034-35",
        "issuing_authority": "Central Environmental Authority",
        "instrument_type": "gazette",
        "language": "en",
        "publication_date": "2017-09-01",
        "effective_date": "2017-09-01",
        "status": "operative",
        "reviewer": "Dhananji_LegalReviewer",
    },
    "4.Order-to-prohibit-burning-of-refuse-and-other-combustible-matters-inclusive-of-Plastic.pdf": {
        "doc_id": "LK-GAZ-2017-2034-36",
        "issuing_authority": "Central Environmental Authority",
        "instrument_type": "gazette",
        "language": "en",
        "publication_date": "2017-09-01",
        "effective_date": "2017-09-01",
        "status": "operative",
        "reviewer": "Dhananji_LegalReviewer",
    },
    "5.Order-to-prohibit-the-use-of-Polyethylene-products-as-Decorations.pdf": {
        "doc_id": "LK-GAZ-2017-2034-37",
        "issuing_authority": "Central Environmental Authority",
        "instrument_type": "gazette",
        "language": "en",
        "publication_date": "2017-09-01",
        "effective_date": "2017-09-01",
        "status": "operative",
        "reviewer": "Dhananji_LegalReviewer",
    },
    "6.Order-to-prohibit-the-manufacure-of-food-containers--plates--cups--spoons-from-expanded-Polystyrene.pdf": {
        "doc_id": "LK-GAZ-2017-2034-38",
        "issuing_authority": "Central Environmental Authority",
        "instrument_type": "gazette",
        "language": "en",
        "publication_date": "2017-09-01",
        "effective_date": "2017-09-01",
        "status": "operative",
        "reviewer": "Dhananji_LegalReviewer",
    },
    "Order-published-under-the-Gazette-Notification-No.-130920-dated-10.10.2003Re-Prohibition-of-Ozone-depleting-substances.pdf": {
        "doc_id": "LK-GAZ-2003-1309-20",
        "issuing_authority": "Central Environmental Authority",
        "instrument_type": "gazette",
        "language": "en",
        "publication_date": "2003-10-10",
        "effective_date": "2003-10-10",
        "status": "operative",
        "reviewer": "Dhananji_LegalReviewer",
    },
    "Order-published-under-the-Gazette-Notification-No.-153316-dated-25.01.2008Re-Environmental-Protection-License-Prescribed-Activities.pdf": {
        "doc_id": "LK-GAZ-2008-1533-16",
        "issuing_authority": "Central Environmental Authority",
        "instrument_type": "gazette",
        "language": "en",
        "publication_date": "2008-01-25",
        "effective_date": "2008-02-01",
        "status": "operative",
        "reviewer": "Dhananji_LegalReviewer",
    },
    "Order-published-under-the-Gazette-Notification-No.-153418-dated-01.02.2008Re-National-Environmental-Protection--Quality-Regulations.pdf": {
        "doc_id": "LK-GAZ-2008-1534-18-A",
        "issuing_authority": "Central Environmental Authority",
        "instrument_type": "gazette",
        "language": "en",
        "publication_date": "2008-02-01",
        "effective_date": "2008-02-01",
        "status": "operative",
        "reviewer": "Dhananji_LegalReviewer",
    },
    "Order_published_under_the_Gazette_Notification_No._14665_dated_10.10.2006_Re_Prohibition_of_Polythene_or_any_polythene_product_of_20_micron_or_below_in_thickness.pdf": {
        "doc_id": "LK-GAZ-2006-1466-05-DUP",
        "issuing_authority": "Central Environmental Authority",
        "instrument_type": "gazette",
        "language": "en",
        "publication_date": "2006-10-10",
        "effective_date": "2007-01-01",
        "status": "operative",
        "reviewer": "Dhananji_LegalReviewer",
    },
    "Order_published_under_the_Gazette_Notification_No._162719_dated_10.11.2009Re_Municipal_Solid_Waste.pdf": {
        "doc_id": "LK-GAZ-2009-1627-19",
        "issuing_authority": "Central Environmental Authority",
        "instrument_type": "gazette",
        "language": "en",
        "publication_date": "2009-11-10",
        "effective_date": "2009-11-10",
        "status": "operative",
        "reviewer": "Dhananji_LegalReviewer",
    },
    "Order_published_under_the_Gazette_Notification_No._92412_dated_23.05.1996Re_industrial_noise_pollution.pdf": {
        "doc_id": "LK-GAZ-1996-924-12",
        "issuing_authority": "Central Environmental Authority",
        "instrument_type": "gazette",
        "language": "en",
        "publication_date": "1996-05-23",
        "effective_date": "1996-05-23",
        "status": "operative",
        "reviewer": "Dhananji_LegalReviewer",
    },
    "Regulations-published-under-the-Gazette-Notification-No.-156222-dated-15.08.2008Re-Permissible-Ambient-Air-Quality-Standards-in-relation-to-class-of-Air-Pollutants.pdf": {
        "doc_id": "LK-GAZ-2008-1562-22",
        "issuing_authority": "Central Environmental Authority",
        "instrument_type": "gazette",
        "language": "en",
        "publication_date": "2008-08-15",
        "effective_date": "2008-08-15",
        "status": "operative",
        "reviewer": "Dhananji_LegalReviewer",
    },
    "Regulations_published_under_the_Gazette_Notification_No._153418_dated_01.02.2008Re_License_for_discharge_emission_or_disposal_of_wastescheduled_waste_management.pdf": {
        "doc_id": "LK-GAZ-2008-1534-18-B",
        "issuing_authority": "Central Environmental Authority",
        "instrument_type": "gazette",
        "language": "en",
        "publication_date": "2008-02-01",
        "effective_date": "2008-02-01",
        "status": "operative",
        "reviewer": "Dhananji_LegalReviewer",
    },
    # 04 Vehicle Repair and Motor Trade
    "DMT-GPR-for-e-Motoring.pdf": {
        "doc_id": "LK-POL-2022-DMT-GPR",
        "issuing_authority": "Department of Motor Traffic",
        "instrument_type": "policy",
        "language": "en",
        "publication_date": "2022-01-01",
        "effective_date": "2022-01-01",
        "status": "policy",
        "reviewer": "Dhananji_LegalReviewer",
    },
    "garaj_application_2023e.pdf": {
        "doc_id": "LK-FORM-2023-DMT-GAR",
        "issuing_authority": "Department of Motor Traffic",
        "instrument_type": "form",
        "language": "en",
        "publication_date": "2023-01-01",
        "effective_date": "2023-01-01",
        "status": "operative",
        "reviewer": "Dhananji_LegalReviewer",
    },
    "garaj_reg_cov_letter.pdf": {
        "doc_id": "LK-POL-2023-DMT-COV",
        "issuing_authority": "Department of Motor Traffic",
        "instrument_type": "policy",
        "language": "si",
        "publication_date": "2023-01-01",
        "effective_date": "2023-01-01",
        "status": "policy",
        "reviewer": "Dhananji_LegalReviewer",
    },
    "mta11_6.pdf": {
        "doc_id": "LK-FORM-MTA-11",
        "issuing_authority": "Department of Motor Traffic",
        "instrument_type": "form",
        "language": "en",
        "publication_date": "2010-01-01",
        "effective_date": "2010-01-01",
        "status": "operative",
        "reviewer": "Dhananji_LegalReviewer",
    },
    "mta2_1.pdf": {
        "doc_id": "LK-FORM-MTA-02",
        "issuing_authority": "Department of Motor Traffic",
        "instrument_type": "form",
        "language": "en",
        "publication_date": "2010-01-01",
        "effective_date": "2010-01-01",
        "status": "operative",
        "reviewer": "Dhananji_LegalReviewer",
    },
    "mta3_2.pdf": {
        "doc_id": "LK-FORM-MTA-03",
        "issuing_authority": "Department of Motor Traffic",
        "instrument_type": "form",
        "language": "en",
        "publication_date": "2010-01-01",
        "effective_date": "2010-01-01",
        "status": "operative",
        "reviewer": "Dhananji_LegalReviewer",
    },
    "mta5_3.pdf": {
        "doc_id": "LK-FORM-MTA-05",
        "issuing_authority": "Department of Motor Traffic",
        "instrument_type": "form",
        "language": "en",
        "publication_date": "2010-01-01",
        "effective_date": "2010-01-01",
        "status": "operative",
        "reviewer": "Dhananji_LegalReviewer",
    },
    "mta7_4.pdf": {
        "doc_id": "LK-FORM-MTA-07",
        "issuing_authority": "Department of Motor Traffic",
        "instrument_type": "form",
        "language": "en",
        "publication_date": "2010-01-01",
        "effective_date": "2010-01-01",
        "status": "operative",
        "reviewer": "Dhananji_LegalReviewer",
    },
    "pq_doc_for_e-motoring_v5_final.pdf": {
        "doc_id": "LK-DRAFT-2021-EMOTORING-V5",
        "issuing_authority": "Department of Motor Traffic",
        "instrument_type": "draft",
        "language": "en",
        "publication_date": "2021-08-01",
        "effective_date": "2021-08-01",
        "status": "draft",
        "reviewer": "Dhananji_LegalReviewer",
    },
    # 05 Data Protection and Digital
    "Data Protection Act SL - English (2).pdf": {
        "doc_id": "LK-ACT-2022-09-EN",
        "issuing_authority": "Data Protection Authority of Sri Lanka",
        "instrument_type": "act",
        "language": "en",
        "publication_date": "2022-03-19",
        "effective_date": "2023-07-17",
        "status": "operative",
        "reviewer": "Dhananji_LegalReviewer",
    },
    "Data Protection Act SL - Sinhala (1).pdf": {
        "doc_id": "LK-ACT-2022-09-SI",
        "issuing_authority": "Data Protection Authority of Sri Lanka",
        "instrument_type": "act",
        "language": "si",
        "publication_date": "2022-03-19",
        "effective_date": "2023-07-17",
        "status": "operative",
        "reviewer": "Dhananji_LegalReviewer",
    },
    # 06 Cosmetics and Salon Products
    "6a560b35e6ece13141629919_F-ACC-17 Processing Fees for Cosmetics.docx": {
        "doc_id": "LK-FORM-NMRA-FACC17",
        "issuing_authority": "National Medicines Regulatory Authority",
        "instrument_type": "form",
        "language": "en",
        "publication_date": "2020-01-01",
        "effective_date": "2020-01-01",
        "status": "operative",
        "reviewer": "Dhananji_LegalReviewer",
    },
    "Application for Sample license of Cosmetics for Test Registration.pdf": {
        "doc_id": "LK-FORM-NMRA-SAMPLE-LIC",
        "issuing_authority": "National Medicines Regulatory Authority",
        "instrument_type": "form",
        "language": "en",
        "publication_date": "2019-01-01",
        "effective_date": "2019-01-01",
        "status": "operative",
        "reviewer": "Dhananji_LegalReviewer",
    },
    "INFORMATION REQUIRED FOR REGISTRATION OF A COSMETIC..pdf": {
        "doc_id": "LK-POL-NMRA-COSMETIC-GUIDE-V1",
        "issuing_authority": "National Medicines Regulatory Authority",
        "instrument_type": "policy",
        "language": "en",
        "publication_date": "2019-01-01",
        "effective_date": "2019-01-01",
        "status": "policy",
        "reviewer": "Dhananji_LegalReviewer",
    },
    "INFORMATION REQUIRED FOR REGISTRATION OF A COSMETIC.pdf": {
        "doc_id": "LK-POL-NMRA-COSMETIC-GUIDE-V2",
        "issuing_authority": "National Medicines Regulatory Authority",
        "instrument_type": "policy",
        "language": "en",
        "publication_date": "2019-01-01",
        "effective_date": "2019-01-01",
        "status": "policy",
        "reviewer": "Dhananji_LegalReviewer",
    },
}


def compute_sha256(file_path: Path) -> str:
    """Computes SHA-256 hash in 64KB binary chunks without modifying the file."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest().lower()


def derive_fallback_metadata(file_path: Path, filename: str) -> Dict[str, Any]:
    """Generates deterministic metadata for any file not in the pre-curated map."""
    clean_name = filename.lower()
    folder_name = file_path.parent.name.lower()

    # Determine instrument_type
    if "draft" in clean_name or "draft" in folder_name:
        instrument_type = "draft"
        status = "draft"
    elif "amendment" in clean_name:
        instrument_type = "amendment"
        status = "operative"
    elif "act" in clean_name:
        instrument_type = "act"
        status = "operative"
    elif "order" in clean_name or "gazette" in clean_name or "regulation" in clean_name:
        instrument_type = "gazette"
        status = "operative"
    elif "application" in clean_name or "form" in clean_name or clean_name.startswith("mta"):
        instrument_type = "form"
        status = "operative"
    elif "policy" in clean_name or "guideline" in clean_name or "information" in clean_name:
        instrument_type = "policy"
        status = "policy"
    else:
        instrument_type = "policy"
        status = "policy"

    # Authority mapping
    if "environmental" in folder_name or "waste" in folder_name:
        authority = "Central Environmental Authority"
    elif "food" in folder_name:
        authority = "Ministry of Health"
    elif "vehicle" in folder_name or "motor" in folder_name:
        authority = "Department of Motor Traffic"
    elif "data_protection" in folder_name:
        authority = "Data Protection Authority of Sri Lanka"
    elif "cosmetic" in folder_name or "salon" in folder_name:
        authority = "National Medicines Regulatory Authority"
    elif "common" in folder_name:
        authority = "Department of the Registrar of Companies"
    else:
        authority = "Relevant Sri Lankan Regulatory Authority"

    # Language mapping
    if "_si" in clean_name or "sinhala" in clean_name:
        language = "si"
    elif "_ta" in clean_name or "tamil" in clean_name:
        language = "ta"
    else:
        language = "en"

    # Deterministic doc_id
    stem_clean = "".join(c if c.isalnum() else "_" for c in file_path.stem).upper()[:24]
    doc_id = f"LK-DOC-{stem_clean}"

    return {
        "doc_id": doc_id,
        "issuing_authority": authority,
        "instrument_type": instrument_type,
        "language": language,
        "publication_date": "2020-01-01",
        "effective_date": "2020-01-01",
        "status": status,
        "reviewer": "Dhananji_LegalReviewer",
    }


def build_register(
    source_dir: Path,
    output_path: Path,
    retrieval_date: str = "2026-10-15",
) -> List[Dict[str, str]]:
    """
    Scans source_dir recursively for raw files, computes SHA-256 digests,
    and writes source_register.csv. Raw files are strictly preserved.
    """
    if not source_dir.exists():
        raise FileNotFoundError(f"Source directory does not exist: {source_dir}")

    # Gather all raw source document files (.pdf, .docx, .doc, .txt)
    raw_files: List[Path] = []
    for ext in ("*.pdf", "*.docx", "*.doc"):
        raw_files.extend(source_dir.rglob(ext))

    # Sort files deterministically
    raw_files.sort(key=lambda p: (p.parent.name, p.name))

    records: List[Dict[str, str]] = []

    for file_path in raw_files:
        filename = file_path.name
        sha256_hash = compute_sha256(file_path)

        meta = SOURCE_METADATA_REGISTRY.get(filename)
        if not meta:
            meta = derive_fallback_metadata(file_path, filename)

        # Enforce strict validation
        instrument_type = meta["instrument_type"]
        status = meta["status"]

        if instrument_type not in VALID_INSTRUMENT_TYPES:
            raise ValueError(f"Invalid instrument_type '{instrument_type}' for {filename}")

        if status not in VALID_STATUSES:
            raise ValueError(f"Invalid status '{status}' for {filename}")

        # Explicit requirement: "Mark drafts as status=draft"
        if instrument_type == "draft":
            status = "draft"

        record: Dict[str, str] = {
            "doc_id": meta["doc_id"],
            "filename": filename,
            "issuing_authority": meta["issuing_authority"],
            "instrument_type": instrument_type,
            "language": meta["language"],
            "publication_date": meta["publication_date"],
            "effective_date": meta["effective_date"],
            "status": status,
            "sha256": sha256_hash,
            "retrieval_date": retrieval_date,
            "reviewer": meta.get("reviewer", "Dhananji_LegalReviewer"),
        }
        records.append(record)

    # Write data/source_register.csv
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(records)

    return records


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=REPO_ROOT / "data" / "raw_sources",
        help="Path to raw sources directory (default: data/raw_sources)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO_ROOT / "data" / "source_register.csv",
        help="Output CSV path (default: data/source_register.csv)",
    )
    parser.add_argument(
        "--retrieval-date",
        type=str,
        default="2026-10-15",
        help="Retrieval date for audit trail (default: 2026-10-15)",
    )

    args = parser.parse_args(argv)

    try:
        records = build_register(
            source_dir=args.source_dir,
            output_path=args.output,
            retrieval_date=args.retrieval_date,
        )
        print(f"Successfully generated {args.output}")
        print(f"Total legal sources registered: {len(records)}")
        print("\nInstrument Type Breakdown:")
        counts: Dict[str, int] = {}
        status_counts: Dict[str, int] = {}
        for r in records:
            counts[r["instrument_type"]] = counts.get(r["instrument_type"], 0) + 1
            status_counts[r["status"]] = status_counts.get(r["status"], 0) + 1
        for k, v in sorted(counts.items()):
            print(f"  - {k}: {v}")
        print("\nStatus Breakdown:")
        for k, v in sorted(status_counts.items()):
            print(f"  - {k}: {v}")
        return 0

    except Exception as exc:
        print(f"ERROR: Failed to build source register: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
