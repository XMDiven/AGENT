from rag_app.config import config
from rag_app.infrastructure.vectore_store import get_vector_store


def get_retriever(top_k: int | None = None):
    vector_store = get_vector_store()
    effective_top_k = top_k if top_k is not None else config.RETRIEVAL_TOP_K

    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": effective_top_k},
    )

    return retriever
