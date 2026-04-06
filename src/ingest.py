from langchain_community.document_loaders import Docx2txtLoader
from langchain_core.documents import Document

from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.clients import get_vector_store

from  src import config
def load_documents(path : str) -> list[Document]:
        loader = Docx2txtLoader(path)
        documents = loader.load()
        return documents

def split_documents(documents : list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
    )

    chunks = splitter.split_documents(documents)
    return chunks

def ingest(path : str):
    documents = load_documents(path)
    chunks = split_documents(documents)
    vector_store = get_vector_store()

    vector_store.add_documents(
        documents=chunks,

    )



