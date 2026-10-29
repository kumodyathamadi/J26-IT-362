"""Local regulatory-text retrieval with optional ChromaDB/SentenceTransformers."""

from __future__ import annotations

import hashlib
import json
import logging
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Tuple

from backend.app.compliance.legal_sources import get_legal_source_inventory
from backend.app.compliance.source_registry import get_source_details

logger = logging.getLogger(__name__)

_REPO_ROOT = Path(__file__).resolve().parents[3]
_CORPUS_DIR = _REPO_ROOT / "sources"
_CHROMA_DIR = _REPO_ROOT / "data" / "compliance" / "chroma"
_SOURCE_IDS = {
    "business_names_statute_1990": "SL-WESTERNPROV-BUSINESSNAMES-1990",
    "cmc_trade_licence_bylaws": "SL-CMC-TRADELIC-1980",
    "food_control_act_1980": "SL-FOODCONTROL-ACT-1980",
}
_TOKEN_PATTERN = re.compile(r"[a-z0-9]+", re.IGNORECASE)
_CHUNK_SIZE = 900
_indexed_corpus_signature: str | None = None


def _source_chunks() -> List[Tuple[str, str, Dict[str, Any]]]:
    chunks: List[Tuple[str, str, Dict[str, Any]]] = []
    for source_path in sorted(_CORPUS_DIR.rglob("*.txt")):
        try:
            content = source_path.read_text(encoding="utf-8").strip()
        except UnicodeDecodeError:
            content = source_path.read_text(encoding="cp1252").strip()
        except OSError:
            logger.exception("Could not read text source %s", source_path)
            continue
        if not content:
            continue
        source_id = _SOURCE_IDS.get(source_path.stem, f"UNREGISTERED-{source_path.stem}")
        source = get_source_details(source_id)
        paragraphs = [part.strip() for part in re.split(r"\n\s*\n", content) if part.strip()]
        source_chunks: List[str] = []
        for paragraph in paragraphs:
            source_chunks.extend(
                paragraph[index : index + _CHUNK_SIZE]
                for index in range(0, len(paragraph), _CHUNK_SIZE)
            )
        for index, text in enumerate(source_chunks):
            chunk_id = hashlib.sha256(
                f"{source_path.name}:{index}:{text}".encode("utf-8")
            ).hexdigest()
            title = next(
                (
                    line.strip()
                    for line in content.splitlines()
                    if line.strip() and "placeholder" not in line.lower()
                ),
                source_path.stem.replace("_", " ").title(),
            )
            metadata = {
                "source_id": source_id,
                "source_title": title,
                "authority": source.get("authority", "Unverified source"),
                "url": source.get("url", ""),
                "effective_date": source.get("effective_date", ""),
                "reviewer_status": "draft",
                "contains_placeholder": "placeholder" in content.lower(),
                "corpus_file": source_path.relative_to(_CORPUS_DIR).as_posix(),
                "file_type": "txt",
            }
            chunks.append((chunk_id, text, metadata))
    return chunks


def _lexical_search(query: str, top_k: int) -> List[Dict[str, Any]]:
    query_tokens = set(_TOKEN_PATTERN.findall(query.lower()))
    if not query_tokens:
        return []

    ranked: List[Tuple[float, str, Dict[str, Any]]] = []
    for chunk_id, text, metadata in _source_chunks():
        text_tokens = set(_TOKEN_PATTERN.findall(text.lower()))
        score = len(query_tokens.intersection(text_tokens)) / len(query_tokens)
        if score > 0:
            ranked.append((score, text, metadata | {"chunk_id": chunk_id}))
    ranked.sort(key=lambda item: item[0], reverse=True)
    return [
        {"score": score, "text": text, "metadata": metadata}
        for score, text, metadata in ranked[:top_k]
    ]


def _legal_source_chunks() -> List[Tuple[str, str, Dict[str, Any]]]:
    """Load extracted legal evidence, retaining its page or text paragraph reference."""
    chunks: List[Tuple[str, str, Dict[str, Any]]] = []
    inventory = get_legal_source_inventory()
    for source in inventory.sources:
        if source.extraction_status != "extracted" or not source.processed_text_path:
            continue
        processed_path = _REPO_ROOT / source.processed_text_path
        if not processed_path.is_file():
            raise FileNotFoundError(
                f"Processed text for legal source {source.source_id} is missing: "
                f"{processed_path}"
            )
        try:
            document = json.loads(processed_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise RuntimeError(
                f"Processed text for legal source {source.source_id} is unreadable"
            ) from exc
        if document.get("file_checksum") != source.file_checksum:
            raise RuntimeError(
                f"Processed text checksum mismatch for legal source {source.source_id}"
            )
        references = [
            (
                int(page["page_number"]),
                None,
                None,
                str(page.get("text") or "").strip(),
            )
            for page in document.get("pages", [])
        ]
        references.extend(
            (
                None,
                segment.get("section_reference"),
                segment.get("paragraph_number"),
                str(segment.get("text") or "").strip(),
            )
            for segment in document.get("segments", [])
        )
        for page_number, section_reference, paragraph_number, text in references:
            if not text:
                continue
            for index in range(0, len(text), _CHUNK_SIZE):
                excerpt = text[index : index + _CHUNK_SIZE]
                chunk_id = hashlib.sha256(
                    f"{source.source_id}:{page_number}:{section_reference}:"
                    f"{paragraph_number}:{index}:{excerpt}".encode("utf-8")
                ).hexdigest()
                chunks.append(
                    (
                        chunk_id,
                        excerpt,
                        {
                            "source_id": source.source_id,
                            "source_title": source.title,
                            "authority": source.issuing_authority or "",
                            "url": source.official_url or "",
                            "effective_date": source.document_date or "",
                            "reviewer_status": (
                                "verified"
                                if source.verification_status == "verified"
                                else "draft"
                            ),
                            "verification_status": source.verification_status,
                            "title_is_filename_guess": source.title_is_filename_guess,
                            "contains_placeholder": "placeholder" in text.lower(),
                            "page": page_number,
                            "section_reference": section_reference,
                            "paragraph_number": paragraph_number,
                            "file_type": source.file_type,
                            "corpus_file": source.source_paths[0],
                        },
                    )
                )
    return chunks


def retrieve_legal_candidates(
    query: str,
    top_k: int = 5,
    source_id: str | None = None,
) -> Dict[str, Any]:
    """Find extracted legal excerpts without asserting they establish law."""
    if top_k < 1 or top_k > 10:
        raise ValueError("top_k must be between 1 and 10")
    query_tokens = set(_TOKEN_PATTERN.findall(query.lower()))
    if not query_tokens:
        return {"mode": "lexical_legal_source_candidates", "evidence": []}

    ranked: List[Tuple[float, str, Dict[str, Any]]] = []
    for chunk_id, text, metadata in _legal_source_chunks():
        if source_id and metadata["source_id"] != source_id:
            continue
        text_tokens = set(_TOKEN_PATTERN.findall(text.lower()))
        score = len(query_tokens.intersection(text_tokens)) / len(query_tokens)
        if score:
            ranked.append((score, text, metadata | {"chunk_id": chunk_id}))
    ranked.sort(key=lambda item: (-item[0], item[2]["source_id"], item[2]["page"]))
    return {
        "mode": "lexical_legal_source_candidates",
        "evidence": [
            {"score": score, "text": text, "metadata": metadata}
            for score, text, metadata in ranked[:top_k]
        ],
    }


@lru_cache(maxsize=1)
def _vector_components() -> Tuple[Any, Any]:
    """Create local-only embedding and persistent vector-store clients on first use."""
    import chromadb
    from sentence_transformers import SentenceTransformer

    _CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(_CHROMA_DIR))
    collection = client.get_or_create_collection(
        name="component2_regulatory_chunks",
        metadata={"hnsw:space": "cosine"},
    )
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return collection, model


def _vector_search(query: str, top_k: int) -> List[Dict[str, Any]]:
    global _indexed_corpus_signature
    chunks = _source_chunks()
    if not chunks:
        return []

    collection, model = _vector_components()
    signature_payload = [
        {"id": chunk_id, "metadata": metadata}
        for chunk_id, _, metadata in chunks
    ]
    signature = hashlib.sha256(
        json.dumps(signature_payload, sort_keys=True).encode("utf-8")
    ).hexdigest()
    if signature != _indexed_corpus_signature:
        ids = [chunk_id for chunk_id, _, _ in chunks]
        documents = [text for _, text, _ in chunks]
        metadatas = [metadata for _, _, metadata in chunks]
        embeddings = model.encode(documents, normalize_embeddings=True).tolist()
        stored_ids = collection.get()["ids"]
        stale_ids = set(stored_ids).difference(ids)
        if stale_ids:
            collection.delete(ids=list(stale_ids))
        collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings,
        )
        _indexed_corpus_signature = signature

    query_embedding = model.encode([query], normalize_embeddings=True).tolist()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=min(top_k, len(chunks)),
        include=["documents", "metadatas", "distances"],
    )
    documents_result = results["documents"][0] or []
    metadata_result = results["metadatas"][0] or []
    distances = results["distances"][0] or []
    return [
        {
            "score": max(0.0, min(1.0, 1.0 - float(distance))),
            "text": document,
            "metadata": metadata,
        }
        for document, metadata, distance in zip(
            documents_result, metadata_result, distances
        )
    ]


def retrieve_evidence(query: str, top_k: int = 3) -> Dict[str, Any]:
    """Retrieve source excerpts; expose the retrieval mode and draft status explicitly."""
    if top_k < 1 or top_k > 10:
        raise ValueError("top_k must be between 1 and 10")

    try:
        evidence = _vector_search(query, top_k)
        return {"mode": "chroma_sentence_transformers", "evidence": evidence}
    except Exception as exc:
        logger.warning(
            "ChromaDB or vector retrieval failed (%s); falling back to labeled lexical retrieval",
            exc,
        )
        return {
            "mode": "lexical_fallback",
            "evidence": _lexical_search(query, top_k),
        }

