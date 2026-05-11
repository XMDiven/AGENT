from rag_app.ingestion.chunkers.pdf_chunker import chunk_pdf
from rag_app.ingestion.loaders.pdf_loader import load_pdf

from rag_app.ingestion.loaders.markdown_loader import load_markdown
from rag_app.ingestion.chunkers.markdown_chunker import chunk_markdown
from rag_app.infrastructure.vectore_store import ingest_chunks

def ingest_markdown_file(path : str) ->dict[str, str | int]:
    documents = load_markdown(path)
    chunks = chunk_markdown(documents)
    ids = ingest_chunks(chunks)

    return {
        "path": str(path),
        "document_count": len(documents),
        "chunk_count": len(chunks),
        "stored_count": len(ids),
    }

def ingest_pdf_file(path : str) ->dict[str, str | int]:
    documents = load_pdf(path)
    chunks = chunk_pdf(documents)
    ids = ingest_chunks(chunks)

    return {
        "path": str(path),
        "document_count": len(documents),
        "chunk_count": len(chunks),
        "stored_count": len(ids),
    }
