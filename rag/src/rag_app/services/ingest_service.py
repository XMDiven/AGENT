import logging
from pathlib import Path
from time import perf_counter

from rag_app.infrastructure.vector_store import ingest_chunks
from rag_app.ingestion.chunkers.markdown_chunker import chunk_markdown
from rag_app.ingestion.chunkers.pdf_chunker import chunk_pdf
from rag_app.ingestion.loaders.markdown_loader import load_markdown
from rag_app.ingestion.loaders.pdf_loader import load_pdf

logger = logging.getLogger(__name__)


def ingest_file(path: str) -> dict[str, str | int]:
    file_path = Path(path)

    if file_path.suffix == ".md":
        return ingest_markdown_file(path)

    if file_path.suffix == ".pdf":
        return ingest_pdf_file(path)

    raise ValueError(f"Unsupported file type: {file_path.suffix}")


def ingest_markdown_file(path: str) -> dict[str, str | int]:
    total_start = perf_counter()

    load_start = perf_counter()
    documents = load_markdown(path)
    load_duration = perf_counter() - load_start

    chunk_start = perf_counter()
    chunks = chunk_markdown(documents)
    chunk_duration = perf_counter() - chunk_start

    store_start = perf_counter()
    ids = ingest_chunks(chunks)
    store_duration = perf_counter() - store_start

    total_duration = perf_counter() - total_start

    logger.info(
        "ingest.completed file_type=markdown path=%s document_count=%s "
        "chunk_count=%s stored_count=%s load_duration_seconds=%.2f "
        "chunk_duration_seconds=%.2f store_duration_seconds=%.2f "
        "total_duration_seconds=%.2f",
        path,
        len(documents),
        len(chunks),
        len(ids),
        load_duration,
        chunk_duration,
        store_duration,
        total_duration,
    )

    return {
        "path": str(path),
        "document_count": len(documents),
        "chunk_count": len(chunks),
        "stored_count": len(ids),
    }


def ingest_pdf_file(path: str) -> dict[str, str | int]:
    total_start = perf_counter()

    load_start = perf_counter()
    documents = load_pdf(path)
    load_duration = perf_counter() - load_start

    chunk_start = perf_counter()
    chunks = chunk_pdf(documents)
    chunk_duration = perf_counter() - chunk_start

    store_start = perf_counter()
    ids = ingest_chunks(chunks)
    store_duration = perf_counter() - store_start

    total_duration = perf_counter() - total_start

    logger.info(
        "ingest.completed file_type=pdf path=%s document_count=%s "
        "chunk_count=%s stored_count=%s load_duration_seconds=%.2f "
        "chunk_duration_seconds=%.2f store_duration_seconds=%.2f "
        "total_duration_seconds=%.2f",
        path,
        len(documents),
        len(chunks),
        len(ids),
        load_duration,
        chunk_duration,
        store_duration,
        total_duration,
    )

    return {
        "path": str(path),
        "document_count": len(documents),
        "chunk_count": len(chunks),
        "stored_count": len(ids),
    }
