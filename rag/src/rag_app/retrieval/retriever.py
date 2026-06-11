from typing import Any, Literal, cast

from langchain_qdrant import QdrantVectorStore

from rag_app.config import config
from rag_app.infrastructure.vector_store import get_vector_store

from functools import lru_cache

from langchain_classic.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from langchain_core.runnables import Runnable , RunnableLambda

RetrievalSearchType = Literal["similarity", "mmr" , "hybrid"]


def get_configured_search_type() -> RetrievalSearchType:
    search_type = config.RETRIEVAL_SEARCH_TYPE

    if search_type not in ("similarity", "mmr" , "hybrid"):
        raise ValueError(f"Unsupported retrieval search type: {search_type}")

    return cast(RetrievalSearchType, search_type)

@lru_cache(maxsize=1)
def load_corpus_documents() -> tuple[Document , ...]:
    vector_store = get_vector_store()
    collection = config.settings.qdrant_collection

    documents: list[Document] = []
    offset = None

    while True:
        points , offset = vector_store.client.scroll(
            collection_name=collection,
            offset=offset,
            limit=256,
            with_payload=True,
            with_vectors=False,
        )

        for point in points:
            payload = point.payload or {}
            documents.append(
                Document(
                    page_content=payload.get("page_content", ""),
                    metadata=payload.get("metadata", {}) or {},
                )
            )

        if offset is None:
            break

    return tuple(documents)



@lru_cache(maxsize=4)
def _get_bm25_retriever(candidate_k: int) -> BM25Retriever:
    bm25 = BM25Retriever.from_documents(list(load_corpus_documents()))
    bm25.k = candidate_k
    return bm25


def build_hybrid_retriever(
    vector_store: QdrantVectorStore,
    top_k: int,
    candidate_k: int,
    bm25_weight: float,
    dense_weight: float,
) -> Runnable:
    bm25_retriever = _get_bm25_retriever(candidate_k)

    dense_retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": candidate_k},
    )

    ensemble = EnsembleRetriever(
        retrievers=[bm25_retriever, dense_retriever],
        weights=[bm25_weight, dense_weight],
    )

    return ensemble | RunnableLambda(lambda docs: docs[:top_k])


def build_search_kwargs(
    top_k: int | None,
    search_type: RetrievalSearchType | None,
    fetch_k: int | None,
    lambda_mult: float | None,
) -> tuple[RetrievalSearchType, dict[str, Any]]:
    effective_search_type = search_type or get_configured_search_type()
    effective_top_k = top_k if top_k is not None else config.RETRIEVAL_TOP_K
    search_kwargs: dict[str, Any] = {"k": effective_top_k}

    if effective_search_type == "mmr":
        search_kwargs["fetch_k"] = (
            fetch_k if fetch_k is not None else config.RETRIEVAL_FETCH_K
        )
        search_kwargs["lambda_mult"] = (
            lambda_mult
            if lambda_mult is not None
            else config.RETRIEVAL_LAMBDA_MULT
        )
    elif fetch_k is not None or lambda_mult is not None:
        raise ValueError("fetch_k and lambda_mult are only supported for MMR")

    return effective_search_type, search_kwargs


def get_retriever(
    top_k: int | None = None,
    search_type: RetrievalSearchType | None = None,
    fetch_k: int | None = None,
    lambda_mult: float | None = None,
    vector_store: QdrantVectorStore | None = None,
  ):
    vector_store = vector_store or get_vector_store()
    effective_search_type = search_type or get_configured_search_type()

    if effective_search_type == "hybrid":
        if fetch_k is not None or lambda_mult is not None:
            raise ValueError("fetch_k and lambda_mult are only supported for MMR")
        effective_top_k = top_k if top_k is not None else config.RETRIEVAL_TOP_K

        return build_hybrid_retriever(
            vector_store=vector_store,
            top_k=effective_top_k,
            candidate_k=config.RETRIEVAL_HYBRID_CANDIDATE_K,
            bm25_weight=config.RETRIEVAL_HYBRID_BM25_WEIGHT,
            dense_weight=config.RETRIEVAL_HYBRID_DENSE_WEIGHT,
        )
    _ , search_kwargs = build_search_kwargs(
        top_k=top_k,
        search_type=search_type,
        fetch_k=fetch_k,
        lambda_mult=lambda_mult,
    )

    return vector_store.as_retriever(
        search_type=effective_search_type,
        search_kwargs=search_kwargs,
    )