import os
import uuid

import dotenv
from langchain_core.documents import Document
from langchain_qdrant import QdrantVectorStore

from config import config
from src.infrastructure.embedding_client import get_embeddings

dotenv.load_dotenv()


def get_vector_store() -> QdrantVectorStore:
    qdrant_url = os.getenv("QDRANT_URL")
    collection_name = config.COLLECTION_NAME
    if not qdrant_url:
        raise RuntimeError("QDRANT_URL is not set")
    if not collection_name:
        raise RuntimeError("QDRANT_COLLECTION is not set")

    return QdrantVectorStore.from_existing_collection(
        embedding=get_embeddings(),
        collection_name=config.COLLECTION_NAME,
        url=qdrant_url,
    )





def ingest_chunks(chunks: list[Document]) -> list[str]:
    if not chunks:
        return []

    vector_store = get_vector_store()
    ids = [str(uuid.uuid4()) for _ in chunks]

    vector_store.add_documents(
        documents=chunks,
        ids=ids,
    )
    return ids
