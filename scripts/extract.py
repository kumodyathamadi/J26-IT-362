"""
Component 2 — Legal Text Extraction Pipeline (scripts/extract.py)

Extracts reference-preserving legal text from Sri Lankan SME regulatory sources.
- Uses digital text layer (pdftotext CLI / PyMuPDF) if present.
- Falls back to Tesseract OCR (eng+sin+tam) at 300 DPI for scanned pages.
- Detects and skips legacy-font Sinhala PDFs (e.g., FMAbhaya/DL-Araliya ASCII mojibake) and logs them.
- Preserves 1-indexed page numbers so statutory citations point to exact pages.
- Outputs full text (data/text/<doc_id>.txt) plus page-level JSON {doc_id, page, text} (data/text/<doc_id>.json).
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import os
import shutil
import subprocess
import sys
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import pymupdf  # PyMuPDF
from PIL import Image

try:
    import pytesseract
except ImportError:
    pytesseract = None

try:
    import docx
except ImportError:
    docx = None

REPO_ROOT = Path(__file__).resolve().parents[1]

# Auto-locate Tesseract binary on Windows / Linux if pytesseract is available
if pytesseract is not None:
    tesseract_candidates = [
        shutil.which("tesseract"),
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Tesseract-OCR\tesseract.exe"),
    ]
    for candidate in tesseract_candidates:
        if candidate and Path(candidate).is_file():
            pytesseract.pytesseract.tesseract_cmd = str(candidate)
            break

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("extract")

# Known legacy non-Unicode font prefixes used in Sri Lankan official documents
LEGACY_SINHALA_FONTS = (
    "FMABABLD",
    "FMABHAYA",
    "FM_",
    "FM-",
    "FM",
    "DL-",
    "DL_",
    "KAPUTA",
    "WIJEYA",
    "SIN-",
    "ARALIYA",
    "THIBUS",
)


def is_legacy_font_sinhala(doc: pymupdf.Document, language: str) -> Tuple[bool, str]:
    """
    Detects whether a PDF uses legacy ASCII-encoded Sinhala fonts (e.g. FMAbhaya).
    Extracting these fonts yields mojibake ASCII characters rather than searchable Unicode Sinhala.
    """
    detected_legacy_fonts: Set[str] = set()

    for page_idx in range(min(5, len(doc))):
        page = doc[page_idx]
        for font in page.get_fonts():
            font_name = (font[3] or "").upper()
            for prefix in LEGACY_SINHALA_FONTS:
                if prefix in font_name:
                    detected_legacy_fonts.add(font[3])

    if detected_legacy_fonts:
        return True, f"Detected legacy ASCII font(s): {', '.join(sorted(detected_legacy_fonts))}"

    # Secondary heuristic for documents tagged as Sinhala
    if language.lower() in ("si", "sinhala"):
        sample_text = ""
        for page_idx in range(min(3, len(doc))):
            sample_text += doc[page_idx].get_text()

        if len(sample_text.strip()) > 100:
            # Check ratio of Unicode Sinhala code points (U+0D80 to U+0DFF)
            sinhala_unicode_chars = sum(1 for c in sample_text if "\u0D80" <= c <= "\u0DFF")
            ratio = sinhala_unicode_chars / len(sample_text)
            if ratio < 0.05:
                # Text is abundant but lacks Unicode Sinhala glyphs (typical of FMAbhaya ASCII text)
                return True, "Sinhala-tagged document contains non-Unicode legacy character encoding"

    return False, ""


def extract_text_layer_from_page(page: pymupdf.Page, pdf_path: Optional[Path] = None, page_num: int = 1) -> str:
    """
    Extracts text layer from a PDF page using pdftotext CLI if available,
    falling back to high-fidelity PyMuPDF page text extraction.
    """
    # 1. Try pdftotext CLI if installed in system PATH
    pdftotext_cmd = shutil.which("pdftotext")
    if pdftotext_cmd and pdf_path and pdf_path.is_file():
        try:
            proc = subprocess.run(
                [pdftotext_cmd, "-f", str(page_num), "-l", str(page_num), str(pdf_path), "-"],
                capture_output=True,
                check=False,
            )
            if proc.returncode == 0:
                text = proc.stdout.decode("utf-8", errors="replace").strip()
                if len(text) > 10:
                    return text
        except Exception:
            pass

    # 2. PyMuPDF extraction (layout-preserving text layer)
    return page.get_text("text").strip()


def run_ocr_on_page(page: pymupdf.Page, dpi: int = 300, langs: str = "eng+sin+tam") -> str:
    """
    Renders the PDF page at specified DPI (default: 300) and performs OCR using Tesseract.
    """
    if pytesseract is None:
        return "[OCR_UNAVAILABLE: pytesseract not installed]"

    try:
        pix = page.get_pixmap(dpi=dpi)
        img = Image.open(BytesIO(pix.tobytes("png")))

        # Try configured languages
        try:
            return pytesseract.image_to_string(img, lang=langs).strip()
        except pytesseract.TesseractError:
            # Fall back to standard English if Sinhala/Tamil tessdata files are absent on host
            logger.warning("Configured languages (%s) unavailable in Tesseract; falling back to 'eng'", langs)
            return pytesseract.image_to_string(img, lang="eng").strip()
    except Exception as exc:
        logger.warning("OCR failed on page %d: %s", page.number + 1, exc)
        return f"[OCR_ERROR: {exc}]"


def extract_pdf_document(
    pdf_path: Path,
    doc_id: str,
    language: str,
    dpi: int,
    langs: str,
) -> Tuple[Optional[List[Dict[str, Any]]], Optional[str]]:
    """
    Extracts all pages from a PDF.
    Returns:
        (pages_list, None) on success
        (None, skip_reason) if skipped (e.g. legacy-font Sinhala)
    """
    doc = pymupdf.open(pdf_path)
    try:
        # Check for legacy font
        is_legacy, legacy_reason = is_legacy_font_sinhala(doc, language)
        if is_legacy:
            return None, legacy_reason

        pages: List[Dict[str, Any]] = []

        for page_idx in range(len(doc)):
            page_num = page_idx + 1  # 1-indexed page number
            page = doc[page_idx]

            # 1. Check if digital text layer exists
            text = extract_text_layer_from_page(page, pdf_path=pdf_path, page_num=page_num)

            # 2. If text layer is missing or near-empty, fallback to Tesseract OCR at 300 DPI
            if len(text.strip()) < 30:
                logger.info("Page %d of %s has no text layer; running OCR at %d DPI...", page_num, doc_id, dpi)
                text = run_ocr_on_page(page, dpi=dpi, langs=langs)

            pages.append({
                "doc_id": doc_id,
                "page": page_num,
                "text": text,
            })

        return pages, None
    finally:
        doc.close()


def extract_docx_document(docx_path: Path, doc_id: str) -> List[Dict[str, Any]]:
    """Extracts text from a DOCX document into a single page-level record."""
    if docx is None:
        return [{"doc_id": doc_id, "page": 1, "text": "[DOCX_PARSER_UNAVAILABLE]"}]

    doc = docx.Document(docx_path)
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

    # Also capture table contents
    for table in doc.tables:
        for row in table.rows:
            row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
            if row_text:
                paragraphs.append(row_text)

    full_text = "\n\n".join(paragraphs)
    return [{
        "doc_id": doc_id,
        "page": 1,
        "text": full_text,
    }]


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--register",
        type=Path,
        default=REPO_ROOT / "data" / "source_register.csv",
        help="Path to source register CSV (default: data/source_register.csv)",
    )
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=REPO_ROOT / "data" / "raw_sources",
        help="Path to raw sources folder (default: data/raw_sources)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=REPO_ROOT / "data" / "text",
        help="Output directory for text and JSON (default: data/text)",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=300,
        help="DPI for rasterizing pages before OCR (default: 300)",
    )
    parser.add_argument(
        "--ocr-langs",
        type=str,
        default="eng+sin+tam",
        help="Tesseract language code string (default: eng+sin+tam)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-extraction of existing files",
    )

    args = parser.parse_args(argv)

    if not args.register.is_file():
        logger.error("Source register not found at %s. Run scripts/build_register.py first.", args.register)
        return 1

    args.output_dir.mkdir(parents=True, exist_ok=True)
    skipped_log_path = args.output_dir / "skipped_legacy_fonts.log"

    # Read registered sources
    with open(args.register, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        sources = list(reader)

    total_sources = len(sources)
    logger.info("Starting text extraction for %d registered sources...", total_sources)

    extracted_count = 0
    skipped_count = 0
    skipped_records: List[Dict[str, str]] = []

    for source in sources:
        doc_id = source["doc_id"]
        filename = source["filename"]
        language = source.get("language", "en")

        txt_out = args.output_dir / f"{doc_id}.txt"
        json_out = args.output_dir / f"{doc_id}.json"
        jsonl_out = args.output_dir / f"{doc_id}.jsonl"

        if txt_out.exists() and json_out.exists() and not args.force:
            logger.info("Skipping already extracted source: %s (%s)", doc_id, filename)
            extracted_count += 1
            continue

        # Locate raw file
        matches = list(args.raw_dir.rglob(filename))
        if not matches:
            logger.warning("Raw file '%s' for doc_id '%s' not found under %s", filename, doc_id, args.raw_dir)
            continue

        raw_file = matches[0]
        ext = raw_file.suffix.lower()

        logger.info("Processing [%s]: %s ...", doc_id, filename)

        if ext == ".docx":
            pages = extract_docx_document(raw_file, doc_id)
        elif ext == ".pdf":
            pages, skip_reason = extract_pdf_document(
                pdf_path=raw_file,
                doc_id=doc_id,
                language=language,
                dpi=args.dpi,
                langs=args.ocr_langs,
            )
            if pages is None:
                logger.warning("[SKIPPED LEGACY FONT] %s (%s): %s", doc_id, filename, skip_reason)
                skipped_records.append({
                    "doc_id": doc_id,
                    "filename": filename,
                    "reason": skip_reason,
                })
                skipped_count += 1
                continue
        else:
            logger.warning("Unsupported file extension '%s' for %s", ext, filename)
            continue

        # Write data/text/<doc_id>.json (page-level JSON array [{doc_id, page, text}, ...])
        with open(json_out, "w", encoding="utf-8") as f:
            json.dump(pages, f, indent=2, ensure_ascii=False)

        # Write data/text/<doc_id>.jsonl (one page-level JSON {doc_id, page, text} per line)
        with open(jsonl_out, "w", encoding="utf-8") as f:
            for p in pages:
                f.write(json.dumps(p, ensure_ascii=False) + "\n")

        # Write data/text/<doc_id>.txt (human-readable text preserving page markers)
        with open(txt_out, "w", encoding="utf-8") as f:
            for p in pages:
                f.write(f"--- PAGE {p['page']} ---\n")
                f.write(p["text"] or "")
                f.write("\n\n")

        extracted_count += 1
        logger.info("Successfully extracted %s -> %d pages saved.", doc_id, len(pages))

    # Record skipped legacy fonts log
    with open(skipped_log_path, "w", encoding="utf-8") as f:
        f.write("# Component 2: Skipped Legacy-Font Sinhala Sources\n")
        f.write("# These PDFs use non-Unicode legacy glyph encodings (e.g. FMAbhaya) and must be converted via glyph re-mappers.\n\n")
        for s in skipped_records:
            f.write(f"doc_id: {s['doc_id']}\n")
            f.write(f"filename: {s['filename']}\n")
            f.write(f"reason: {s['reason']}\n")
            f.write("-" * 60 + "\n")

    logger.info("=" * 60)
    logger.info("EXTRACTION SUMMARY:")
    logger.info("  Total sources: %d", total_sources)
    logger.info("  Extracted sources: %d", extracted_count)
    logger.info("  Skipped legacy-font PDFs: %d (logged to %s)", skipped_count, skipped_log_path)
    logger.info("=" * 60)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
