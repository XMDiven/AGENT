from langchain_core.documents import Document

from src.clients import get_vector_store

from src import config
def get_retriever():
    vector_store = get_vector_store()

    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={
            "k": config.RETRIEVAL_TOP_K
        },
    )
    return retriever
def retrieve_documents(question: str) -> list[Document]:
    retriever = get_retriever()
    documents = retriever.invoke(question)
    return documents




