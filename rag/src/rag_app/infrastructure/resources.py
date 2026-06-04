from dataclasses import dataclass

from langchain_openai import ChatOpenAI
from langchain_qdrant import QdrantVectorStore

from rag_app.infrastructure.llm_client import get_client
from rag_app.infrastructure.vector_store import get_vector_store


@dataclass(frozen=True)
class AppResources:
    llm_client: ChatOpenAI
    vector_store: QdrantVectorStore


def create_app_resources() -> AppResources:
    return AppResources(
        llm_client=get_client(),
        vector_store=get_vector_store(),
    )
