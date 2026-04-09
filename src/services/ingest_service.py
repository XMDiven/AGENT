from src.ingestion.loaders.markdown_loader import load_markdown
from src.ingestion.chunkers.markdown_chunker import chunk_markdown
from src.infrastructure.vectore_store import ingest_chunks
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