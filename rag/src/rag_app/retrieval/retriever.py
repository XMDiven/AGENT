from typing import Any, Literal, cast

from langchain_qdrant import QdrantVectorStore

from rag_app.config import config
from rag_app.infrastructure.vector_store import get_vector_store

RetrievalSearchType = Literal["similarity", "mmr"]


def get_configured_search_type() -> RetrievalSearchType:
    search_type = config.RETRIEVAL_SEARCH_TYPE

    if search_type not in ("similarity", "mmr"):
        raise ValueError(f"Unsupported retrieval search type: {search_type}")

    return cast(RetrievalSearchType, search_type)


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
    effective_search_type, search_kwargs = build_search_kwargs(
        top_k=top_k,
        search_type=search_type,
        fetch_k=fetch_k,
        lambda_mult=lambda_mult,
    )

    retriever = vector_store.as_retriever(
        search_type=effective_search_type,
        search_kwargs=search_kwargs,
    )

    return retriever
