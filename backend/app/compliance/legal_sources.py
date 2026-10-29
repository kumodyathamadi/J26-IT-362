"""Idempotent inventory and page-preserving extraction of legal PDF sources."""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import tempfile
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Literal, Optional, Sequence

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

_REPO_ROOT = Path(__file__).resolve().parents[3]
LEGAL_SOURCE_DIR = (
    _REPO_ROOT / "data" / "compliance" / "raw" / "Component2_Legal_Sources"
)
TEXT_SOURCE_DIR = _REPO_ROOT / "sources"
PROCESSED_SOURCE_DIR = _REPO_ROOT / "data" / "compliance" / "processed" / "legal_sources"
INVENTORY_PATH = _REPO_ROOT / "data" / "compliance" / "legal_source_inventory.json"

ExtractionStatus = Literal[
    "not_ingested", "extracted", "empty", "empty_or_scanned", "extraction_error"
]
VerificationStatus = Literal["needs_verification", "verified", "rejected"]


class LegalSourceMetadata(BaseModel):
    source_id: str
    title: str
    issuing_authority: Optional[str] = None
    document_date: Optional[str] = None
    ingestion_date: str
    file_checksum: str
    source_paths: list[str]
    category: str
    file_type: Literal["pdf", "txt"] = "pdf"
    page_count: Optional[int] = None
    page_numbers: list[int] = Field(default_factory=list)
    section_references: list[str] = Field(default_factory=list)
    pages_without_text: list[int] = Field(default_factory=list)
    ocr_recommended: bool = False
    extraction_status: ExtractionStatus = "not_ingested"
    extraction_error: Optional[str] = None
    extraction_timestamp: Optional[str] = None
    text_encoding: Optional[str] = None
    processed_text_path: Optional[str] = None
    official_url: Optional[str] = None
    title_is_filename_guess: bool = True
    verification_status: VerificationStatus = "needs_verification"


class LegalSourceInventory(BaseModel):
    schema_version: int = 1
    sources: list[LegalSourceMetadata] = Field(default_factory=list)


class LegalSourceIngestionResult(BaseModel):
    discovered_files: int
    unique_sources: int
    ingested_sources: int
    skipped_sources: int
    duplicate_files: int
    extraction_errors: int
    sources: list[LegalSourceMetadata]


class PdfExtractionUnavailable(RuntimeError):
    """Raised when PDFs exist but the configured local parser is unavailable."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _source_id(checksum: str, file_type: str = "pdf") -> str:
    return f"SL-C2-{file_type.upper()}-{checksum[:20]}"


def _source_display_path(path: Path, source_root: Path) -> str:
    try:
        return path.relative_to(_REPO_ROOT).as_posix()
    except ValueError:
        return path.relative_to(source_root).as_posix()


def _processed_display_path(path: Path) -> str:
    try:
        return path.relative_to(_REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _read_text_file(path: Path) -> tuple[str, str]:
    content = path.read_bytes()
    if b"\x00" in content:
        raise ValueError("Text file contains binary NUL bytes")
    if content.startswith(b"\xef\xbb\xbf"):
        return content.decode("utf-8-sig"), "utf-8-sig"
    for encoding in ("utf-8", "cp1252", "latin-1"):
        try:
            return content.decode(encoding), encoding
        except UnicodeDecodeError:
            continue
    raise UnicodeError("Text file could not be decoded with supported encodings")


_SECTION_REFERENCE = re.compile(
    r"^\s*((?:section|sec\.?|part|chapter|article|regulation|rule|clause)"
    r"\s+[\w./()\-]+|by-?law(?:\s+section)?\s+[\w./()\-]+|"
    r"order(?:\s+no\.?)?\s+[\w./()\-]+|§\s*[\w./()\-]+)",
    re.IGNORECASE,
)


def _text_segments(text: str) -> tuple[list[dict], list[str]]:
    segments: list[dict] = []
    section_references: list[str] = []
    for paragraph_number, paragraph in enumerate(
        (item.strip() for item in re.split(r"\n\s*\n", text)),
        start=1,
    ):
        if not paragraph:
            continue
        lines = paragraph.splitlines()
        first_line = lines[0].strip()
        reference_match = None
        reference_heading = None
        for line in lines:
            reference_match = _SECTION_REFERENCE.match(line)
            if reference_match:
                reference_heading = line.strip()
                break
        section_reference = reference_match.group(1).strip() if reference_match else None
        if section_reference and section_reference not in section_references:
            section_references.append(section_reference)
        heading = (
            reference_heading or first_line
            if len(reference_heading or first_line) <= 160
            and (reference_match or first_line.isupper())
            else None
        )
        segments.append(
            {
                "paragraph_number": paragraph_number,
                "section_reference": section_reference,
                "heading": heading,
                "text": paragraph,
            }
        )
    return segments, section_references


def _safe_write_json(path: Path, document: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Optional[Path] = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary:
            temporary_path = Path(temporary.name)
            json.dump(document, temporary, ensure_ascii=False, indent=2)
            temporary.write("\n")
        os.replace(temporary_path, path)
    except OSError:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
        raise


def _read_existing_inventory(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as inventory_file:
        document = json.load(inventory_file)
    inventory = LegalSourceInventory.model_validate(document)
    return {source.source_id: source.model_dump() for source in inventory.sources}


def get_legal_source_inventory(
    inventory_path: Path = INVENTORY_PATH,
) -> LegalSourceInventory:
    """Return the saved legal-PDF inventory without scanning or mutating files."""
    if not inventory_path.exists():
        return LegalSourceInventory()
    with inventory_path.open(encoding="utf-8") as inventory_file:
        return LegalSourceInventory.model_validate(json.load(inventory_file))


def ingest_legal_sources(
    source_root: Path = LEGAL_SOURCE_DIR,
    processed_root: Path = PROCESSED_SOURCE_DIR,
    inventory_path: Path = INVENTORY_PATH,
    *,
    additional_source_roots: Optional[Sequence[Path]] = None,
    force: bool = False,
) -> LegalSourceIngestionResult:
    """Extract supported legal files, deduplicate them, and retain source references."""
    if additional_source_roots is None:
        additional_source_roots = (
            (TEXT_SOURCE_DIR,) if source_root == LEGAL_SOURCE_DIR else ()
        )
    source_roots = list(dict.fromkeys((source_root, *additional_source_roots)))
    source_files = sorted(
        (
            (path, root)
            for root in source_roots
            if root.exists()
            for path in root.rglob("*")
            if path.is_file() and path.suffix.lower() in {".pdf", ".txt"}
        ),
        key=lambda item: (
            item[1].as_posix().casefold(),
            item[0].relative_to(item[1]).as_posix().casefold(),
        ),
    )
    if not source_files:
        return LegalSourceIngestionResult(
            discovered_files=0,
            unique_sources=0,
            ingested_sources=0,
            skipped_sources=0,
            duplicate_files=0,
            extraction_errors=0,
            sources=[],
        )

    existing = _read_existing_inventory(inventory_path)
    grouped_paths: dict[str, list[tuple[Path, Path]]] = {}
    for path, root in source_files:
        grouped_paths.setdefault(_sha256(path), []).append((path, root))

    today = date.today().isoformat()
    sources: list[LegalSourceMetadata] = []
    ingested_count = 0
    skipped_count = 0
    error_count = 0

    for checksum, paths in sorted(grouped_paths.items()):
        primary_path, primary_root = paths[0]
        file_type = primary_path.suffix.lower().lstrip(".")
        source_id = _source_id(checksum, file_type)
        previous = existing.get(source_id, {})
        relative_paths = [
            _source_display_path(path, root) for path, root in paths
        ]
        title = primary_path.stem.replace("_", " ").replace("-", " ").strip()
        processed_path = processed_root / f"{source_id}.json"
        previous_is_reusable = (
            not force
            and previous.get("file_checksum") == checksum
            and previous.get("extraction_timestamp")
            and previous.get("extraction_status")
            in {"extracted", "empty", "empty_or_scanned"}
            and processed_path.is_file()
        )

        if previous_is_reusable:
            extraction_status = previous["extraction_status"]
            page_count = previous.get("page_count")
            page_numbers = previous.get("page_numbers", [])
            section_references = previous.get("section_references", [])
            pages_without_text = previous.get("pages_without_text", [])
            extraction_error = None
            extraction_timestamp = previous.get("extraction_timestamp")
            text_encoding = previous.get("text_encoding")
            skipped_count += 1
        else:
            try:
                pages: list[dict] = []
                segments: list[dict] = []
                page_numbers: list[int] = []
                pages_without_text = []
                section_references = []
                text_encoding = None
                if file_type == "pdf":
                    try:
                        import pymupdf as fitz
                    except ImportError as exc:
                        raise PdfExtractionUnavailable(
                            "PDF extraction requires PyMuPDF. Install the backend "
                            "dependencies and retry legal-source ingestion."
                        ) from exc
                    document = fitz.open(primary_path)
                    try:
                        for page_number, page in enumerate(document, start=1):
                            text = page.get_text("text").strip()
                            pages.append({"page_number": page_number, "text": text})
                            if not text:
                                pages_without_text.append(page_number)
                        page_count = len(document)
                    finally:
                        document.close()
                    extraction_status = (
                        "extracted" if any(page["text"] for page in pages)
                        else "empty_or_scanned"
                    )
                else:
                    text, text_encoding = _read_text_file(primary_path)
                    segments, section_references = _text_segments(text)
                    page_count = None
                    extraction_status = "extracted" if segments else "empty"

                extraction_error = None
                _safe_write_json(
                    processed_path,
                    {
                        "source_id": source_id,
                        "file_checksum": checksum,
                        "file_type": file_type,
                        "verification_status": previous.get(
                            "verification_status", "needs_verification"
                        ),
                        "pages": pages,
                        "segments": segments,
                    },
                )
                extraction_timestamp = datetime.now(timezone.utc).isoformat()
                ingested_count += 1
            except PdfExtractionUnavailable:
                raise
            except Exception as exc:
                logger.exception("Could not extract legal source %s", primary_path)
                extraction_status = "extraction_error"
                page_count = None
                page_numbers = []
                section_references = []
                pages_without_text = []
                extraction_error = (
                    f"{type(exc).__name__}: Legal source could not be extracted."
                )
                extraction_timestamp = datetime.now(timezone.utc).isoformat()
                text_encoding = None
                error_count += 1

        record = {
            **previous,
            "source_id": source_id,
            "title": previous.get("title") or title,
            "issuing_authority": previous.get("issuing_authority"),
            "document_date": previous.get("document_date"),
            "ingestion_date": previous.get("ingestion_date") or today,
            "file_checksum": checksum,
            "source_paths": relative_paths,
            "category": (
                primary_path.parent.relative_to(primary_root).as_posix()
                if primary_path.parent != primary_root
                else ""
            ),
            "file_type": file_type,
            "page_count": page_count,
            "page_numbers": list(range(1, page_count + 1)) if page_count is not None else page_numbers,
            "section_references": section_references,
            "pages_without_text": pages_without_text,
            "extraction_status": extraction_status,
            "extraction_error": extraction_error,
            "extraction_timestamp": extraction_timestamp,
            "text_encoding": text_encoding,
            "processed_text_path": (
                _processed_display_path(processed_path)
                if extraction_status in {"extracted", "empty", "empty_or_scanned"}
                else None
            ),
            "official_url": previous.get("official_url"),
            "verification_status": previous.get(
                "verification_status", "needs_verification"
            ),
        }
        record["ocr_recommended"] = bool(pages_without_text)
        sources.append(LegalSourceMetadata.model_validate(record))

    inventory = LegalSourceInventory(sources=sources)
    _safe_write_json(inventory_path, inventory.model_dump())
    return LegalSourceIngestionResult(
        discovered_files=len(source_files),
        unique_sources=len(sources),
        ingested_sources=ingested_count,
        skipped_sources=skipped_count,
        duplicate_files=len(source_files) - len(sources),
        extraction_errors=error_count,
        sources=sources,
    )
