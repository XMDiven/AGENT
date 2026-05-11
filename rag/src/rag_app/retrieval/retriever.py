from rag_app.config import config
from rag_app.infrastructure.vectore_store import get_vector_store


def get_retriever():
    vector_store = get_vector_store()

    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": config.RETRIEVAL_TOP_K}
    )

    return retriever
