import json
import uuid

from langchain_core.documents import Document
from langchain_qdrant import QdrantVectorStore

from rag_app.config import config
from rag_app.infrastructure.embedding_client import get_embeddings


def get_vector_store() -> QdrantVectorStore:
    qdrant_url = config.settings.qdrant_url
    collection_name = config.settings.qdrant_collection

    if not qdrant_url:
        raise RuntimeError("QDRANT_URL is not set")

    if not collection_name:
        raise RuntimeError("QDRANT_COLLECTION is not set")

    return QdrantVectorStore.from_existing_collection(
        embedding=get_embeddings(),
        collection_name=collection_name,
        url=qdrant_url,
    )


def build_chunk_id(document : Document) -> str:
    payload = {
        "source": str(document.metadata.get("source", "")),
        "section_path": str(document.metadata.get("section_path", "")),
        "page": str(document.metadata.get("page", "")),
        "content": document.page_content,
    }

    serialized_payload = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
    )
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, serialized_payload))

def ingest_chunks(
    chunks: list[Document],
    vector_store: QdrantVectorStore | None = None,
) -> list[str]:
    if not chunks:
        return []

    vector_store = vector_store or get_vector_store()

    unique_chunks_by_id: dict[str, Document] = {}

    for chunk in chunks:
        chunk_id = build_chunk_id(chunk)
        unique_chunks_by_id.setdefault(chunk_id, chunk)

    ids = list(unique_chunks_by_id.keys())
    chunks = list(unique_chunks_by_id.values())

    vector_store.add_documents(
        documents=chunks,
        ids=ids,
    )

    return ids
