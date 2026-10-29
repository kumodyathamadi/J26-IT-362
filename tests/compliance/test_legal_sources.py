"""Tests for repeatable, source-grounded legal PDF ingestion."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import pymupdf as fitz
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.app.api.component2_routes import router
import backend.app.compliance.retrieval as retrieval
from backend.app.compliance.legal_sources import (
    LegalSourceInventory,
    LegalSourceMetadata,
    get_legal_source_inventory,
    ingest_legal_sources,
)


def _write_pdf(path: Path, pages: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    document = fitz.open()
    for text in pages:
        page = document.new_page()
        if text:
            page.insert_text((72, 72), text)
    document.save(path)
    document.close()


def test_ingests_recursive_pdfs_with_pages_and_candidate_metadata(tmp_path: Path):
    source_root = tmp_path / "raw"
    _write_pdf(source_root / "food" / "act.pdf", ["Section 1", "Section 2"])
    processed_root = tmp_path / "processed"
    inventory_path = tmp_path / "inventory.json"

    result = ingest_legal_sources(source_root, processed_root, inventory_path)

    assert result.discovered_files == 1
    assert result.unique_sources == 1
    source = result.sources[0]
    assert source.source_id.startswith("SL-C2-PDF-")
    assert len(source.file_checksum) == 64
    assert source.source_paths == ["food/act.pdf"]
    assert source.page_count == 2
    assert source.page_numbers == [1, 2]
    assert source.verification_status == "needs_verification"
    assert source.extraction_status == "extracted"

    extracted = json.loads((processed_root / f"{source.source_id}.json").read_text())
    assert extracted["pages"] == [
        {"page_number": 1, "text": "Section 1"},
        {"page_number": 2, "text": "Section 2"},
    ]
    assert inventory_path.exists()


def test_deduplicates_identical_pdfs_and_skips_unchanged_reingestion(tmp_path: Path):
    source_root = tmp_path / "raw"
    _write_pdf(source_root / "food" / "act.pdf", ["Same PDF content"])
    duplicate = source_root / "other" / "copy.pdf"
    duplicate.parent.mkdir(parents=True)
    duplicate.write_bytes((source_root / "food" / "act.pdf").read_bytes())
    processed_root = tmp_path / "processed"
    inventory_path = tmp_path / "inventory.json"

    first = ingest_legal_sources(source_root, processed_root, inventory_path)
    second = ingest_legal_sources(source_root, processed_root, inventory_path)

    assert first.discovered_files == 2
    assert first.unique_sources == 1
    assert first.duplicate_files == 1
    assert first.ingested_sources == 1
    assert first.sources[0].source_paths == ["food/act.pdf", "other/copy.pdf"]
    assert second.ingested_sources == 0
    assert second.skipped_sources == 1
    assert len(get_legal_source_inventory(inventory_path).sources) == 1
    saved_inventory = json.loads(inventory_path.read_text())
    assert len(saved_inventory["sources"]) == 1


def test_empty_or_scanned_pdf_is_marked_without_claiming_ocr(tmp_path: Path):
    source_root = tmp_path / "raw"
    _write_pdf(source_root / "scanned.pdf", [""])

    result = ingest_legal_sources(
        source_root,
        tmp_path / "processed",
        tmp_path / "inventory.json",
    )

    assert result.sources[0].extraction_status == "empty_or_scanned"
    assert result.sources[0].pages_without_text == [1]
    assert result.sources[0].ocr_recommended is True
    assert result.sources[0].verification_status == "needs_verification"


def test_partially_scanned_pdf_recommends_ocr_for_blank_pages(tmp_path: Path):
    source_root = tmp_path / "raw"
    _write_pdf(source_root / "mixed.pdf", ["Extractable page", ""])

    result = ingest_legal_sources(
        source_root,
        tmp_path / "processed",
        tmp_path / "inventory.json",
    )

    assert result.sources[0].extraction_status == "extracted"
    assert result.sources[0].pages_without_text == [2]
    assert result.sources[0].ocr_recommended is True


def test_corrupt_pdf_failure_is_recorded_and_does_not_abort_batch(tmp_path: Path):
    source_root = tmp_path / "raw"
    _write_pdf(source_root / "valid.pdf", ["Valid text"])
    corrupt = source_root / "corrupt.pdf"
    corrupt.write_bytes(b"not a PDF")

    result = ingest_legal_sources(
        source_root,
        tmp_path / "processed",
        tmp_path / "inventory.json",
    )

    assert result.discovered_files == 2
    assert result.extraction_errors == 1
    assert sum(source.extraction_status == "extraction_error" for source in result.sources) == 1
    assert sum(source.extraction_status == "extracted" for source in result.sources) == 1
    assert next(
        source for source in result.sources
        if source.extraction_status == "extraction_error"
    ).extraction_error


def test_inventory_and_ingestion_api_endpoints(monkeypatch, tmp_path: Path):
    import backend.app.api.component2_routes as component2_routes

    source_root = tmp_path / "raw"
    _write_pdf(source_root / "act.pdf", ["Clause text"])
    processed_root = tmp_path / "processed"
    inventory_path = tmp_path / "inventory.json"
    monkeypatch.setattr(
        component2_routes,
        "get_legal_source_inventory",
        lambda: LegalSourceInventory(),
    )
    monkeypatch.setattr(
        component2_routes,
        "ingest_legal_sources",
        lambda force=False: ingest_legal_sources(
            source_root, processed_root, inventory_path, force=force
        ),
    )
    app = FastAPI()
    app.include_router(router)

    client = TestClient(app)
    assert client.get("/api/v1/component2/sources").status_code == 200
    response = client.post("/api/v1/component2/sources/ingest")

    assert response.status_code == 200
    assert response.json()["discovered_files"] == 1
    assert response.json()["sources"][0]["verification_status"] == "needs_verification"
    assert "processed_text_path" not in response.json()["sources"][0]


def test_source_metadata_and_evidence_endpoints(monkeypatch, tmp_path: Path):
    import backend.app.api.component2_routes as component2_routes

    source_id = "SL-C2-TXT-0123456789abcdef0123"
    source = LegalSourceMetadata(
        source_id=source_id,
        title="candidate_source",
        ingestion_date="2026-10-14",
        file_checksum="c" * 64,
        source_paths=["02_Food_Business/law.txt"],
        category="02_Food_Business",
        file_type="txt",
    )
    inventory = LegalSourceInventory(sources=[source])
    monkeypatch.setattr(
        component2_routes,
        "get_legal_source_inventory",
        lambda: inventory,
    )
    monkeypatch.setattr(
        component2_routes,
        "retrieve_legal_candidates",
        lambda query, top_k, source_id: {
            "mode": "lexical_legal_source_candidates",
            "evidence": [
                {
                    "score": 1.0,
                    "text": "Section 8(2) food premises text.",
                    "metadata": {
                        "source_id": source_id,
                        "page": None,
                        "section_reference": "Section 8(2)",
                        "paragraph_number": 2,
                        "file_type": "txt",
                        "verification_status": "needs_verification",
                    },
                }
            ],
        },
    )
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    metadata_response = client.get(f"/api/v1/component2/sources/{source_id}")
    evidence_response = client.get(
        f"/api/v1/component2/sources/{source_id}/evidence",
        params={"query": "food premises"},
    )
    missing_response = client.get("/api/v1/component2/sources/not-in-inventory")

    assert metadata_response.status_code == 200
    assert metadata_response.json()["file_type"] == "txt"
    assert "processed_text_path" not in metadata_response.json()
    assert evidence_response.status_code == 200
    assert evidence_response.json()["evidence"][0]["metadata"]["section_reference"] == (
        "Section 8(2)"
    )
    assert missing_response.status_code == 404


def test_ingests_nested_text_sources_with_checksum_and_section_references(
    tmp_path: Path,
):
    source_root = tmp_path / "sources"
    text_path = source_root / "02_Food_Business" / "food_act.txt"
    text_path.parent.mkdir(parents=True)
    text_path.write_text(
        "Food Control Act candidate\n"
        "[PLACEHOLDER LEGAL TEXT]\n"
        "Section 2(1):\n"
        "No person shall handle food.",
        encoding="utf-8",
    )
    processed_root = tmp_path / "processed"
    inventory_path = tmp_path / "inventory.json"

    result = ingest_legal_sources(
        source_root,
        processed_root,
        inventory_path,
    )

    assert result.discovered_files == 1
    source = result.sources[0]
    assert source.file_type == "txt"
    assert source.source_id.startswith("SL-C2-TXT-")
    assert source.source_paths == ["02_Food_Business/food_act.txt"]
    assert source.page_count is None
    assert source.section_references == ["Section 2(1)"]
    assert source.extraction_status == "extracted"
    assert source.text_encoding == "utf-8"
    assert source.extraction_timestamp
    assert source.verification_status == "needs_verification"

    extracted = json.loads(
        (processed_root / f"{source.source_id}.json").read_text(encoding="utf-8")
    )
    section_segment = extracted["segments"][0]
    assert section_segment["paragraph_number"] == 1
    assert section_segment["section_reference"] == "Section 2(1)"
    assert section_segment["heading"] == "Section 2(1):"
    assert section_segment["text"].replace("\r\n", "\n") == (
        "Food Control Act candidate\n"
        "[PLACEHOLDER LEGAL TEXT]\n"
        "Section 2(1):\n"
        "No person shall handle food."
    )


def test_force_reprocesses_unchanged_text_source(tmp_path: Path):
    source_root = tmp_path / "sources"
    source_root.mkdir()
    (source_root / "law.txt").write_text("Section 1: Sample text.", encoding="utf-8")
    processed_root = tmp_path / "processed"
    inventory_path = tmp_path / "inventory.json"

    first = ingest_legal_sources(source_root, processed_root, inventory_path)
    forced = ingest_legal_sources(
        source_root,
        processed_root,
        inventory_path,
        force=True,
    )

    assert first.ingested_sources == 1
    assert forced.ingested_sources == 1
    assert forced.skipped_sources == 0


def test_unreadable_binary_text_source_is_recorded_without_aborting_batch(
    tmp_path: Path,
):
    source_root = tmp_path / "sources"
    source_root.mkdir()
    (source_root / "valid.txt").write_text("Valid text", encoding="utf-8")
    (source_root / "binary.txt").write_bytes(b"invalid\x00text")

    result = ingest_legal_sources(
        source_root,
        tmp_path / "processed",
        tmp_path / "inventory.json",
    )

    assert result.discovered_files == 2
    assert result.extraction_errors == 1
    failed_source = next(
        source for source in result.sources
        if source.extraction_status == "extraction_error"
    )
    assert "ValueError" in failed_source.extraction_error


def test_empty_text_file_is_recorded_as_empty_not_as_an_extraction_error(
    tmp_path: Path,
):
    source_root = tmp_path / "sources"
    source_root.mkdir()
    (source_root / "empty.txt").write_bytes(b"")

    result = ingest_legal_sources(
        source_root,
        tmp_path / "processed",
        tmp_path / "inventory.json",
    )

    assert result.extraction_errors == 0
    assert result.sources[0].extraction_status == "empty"
    assert result.sources[0].ocr_recommended is False


def test_source_inventory_paths_exist_and_include_reorganized_text_files():
    repository_root = Path(__file__).resolve().parents[2]
    source_root = repository_root / "sources"
    inventory_path = source_root / "source_inventory.csv"
    with inventory_path.open(encoding="utf-8-sig", newline="") as inventory_file:
        rows = list(csv.DictReader(inventory_file))

    relative_paths = [
        Path(row["category_folder"]) / row["filename"] for row in rows
    ]
    expected_text_sources = {
        Path("01_Common_Business_Registration/business_names_statute_1990.txt"),
        Path("01_Common_Business_Registration/cmc_trade_licence_bylaws.txt"),
        Path("02_Food_Business/food_control_act_1980.txt"),
        Path("03_Environmental_and_Waste/cea_environmental_act_2008.txt"),
        Path("06_Cosmetics_and_Salon_Products/nmra_cosmetics_act_2015.txt"),
    }

    assert len(relative_paths) == len(set(relative_paths))
    assert expected_text_sources <= set(relative_paths)
    explicitly_missing = []
    for row, relative_path in zip(rows, relative_paths):
        assert not relative_path.is_absolute()
        assert ".." not in relative_path.parts
        if (source_root / relative_path).is_file():
            continue
        assert "missing" in row["review_status"].lower()
        explicitly_missing.append(relative_path)
    assert len(explicitly_missing) == 3


def test_pdf_candidate_retrieval_preserves_page_and_unverified_status(
    monkeypatch,
    tmp_path: Path,
):
    source_id = "SL-C2-PDF-0123456789abcdef0123"
    processed_path = tmp_path / "processed.json"
    processed_path.write_text(
        json.dumps(
            {
                "file_checksum": "a" * 64,
                "pages": [
                    {"page_number": 1, "text": "Unrelated information."},
                    {
                        "page_number": 7,
                        "text": "Food premises hygiene and inspection information.",
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    source = LegalSourceMetadata(
        source_id=source_id,
        title="example_filename_title",
        ingestion_date="2026-10-14",
        file_checksum="a" * 64,
        source_paths=["food/example.pdf"],
        category="food",
        page_count=2,
        page_numbers=[1, 2],
        extraction_status="extracted",
        processed_text_path=str(processed_path),
    )
    monkeypatch.setattr(
        retrieval,
        "get_legal_source_inventory",
        lambda: LegalSourceInventory(sources=[source]),
    )

    result = retrieval.retrieve_legal_candidates("food hygiene inspection", top_k=1)

    assert result["mode"] == "lexical_legal_source_candidates"
    assert len(result["evidence"]) == 1
    candidate = result["evidence"][0]
    assert candidate["metadata"]["source_id"] == source_id
    assert candidate["metadata"]["page"] == 7
    assert candidate["metadata"]["verification_status"] == "needs_verification"
    assert candidate["metadata"]["title_is_filename_guess"] is True


def test_text_candidate_retrieval_preserves_section_reference_without_page(
    monkeypatch,
    tmp_path: Path,
):
    source_id = "SL-C2-TXT-0123456789abcdef0123"
    processed_path = tmp_path / "processed.json"
    processed_path.write_text(
        json.dumps(
            {
                "file_checksum": "b" * 64,
                "segments": [
                    {
                        "paragraph_number": 3,
                        "section_reference": "Section 8(2)",
                        "heading": "Section 8(2)",
                        "text": "Section 8(2) food premises hygiene candidate text.",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    source = LegalSourceMetadata(
        source_id=source_id,
        title="candidate_text_source",
        ingestion_date="2026-10-14",
        file_checksum="b" * 64,
        source_paths=["02_Food_Business/example.txt"],
        category="02_Food_Business",
        file_type="txt",
        extraction_status="extracted",
        processed_text_path=str(processed_path),
    )
    monkeypatch.setattr(
        retrieval,
        "get_legal_source_inventory",
        lambda: LegalSourceInventory(sources=[source]),
    )

    result = retrieval.retrieve_legal_candidates("food premises hygiene", top_k=1)

    assert result["evidence"][0]["metadata"]["page"] is None
    assert result["evidence"][0]["metadata"]["section_reference"] == "Section 8(2)"
    assert result["evidence"][0]["metadata"]["paragraph_number"] == 3
    assert result["evidence"][0]["metadata"]["file_type"] == "txt"
