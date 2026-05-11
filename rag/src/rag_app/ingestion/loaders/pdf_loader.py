from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document

from rag_app.ingestion.loaders.source_path import to_project_relative_source


def load_pdf(path : str | Path) -> list[Document]:
    loader = PyPDFLoader(str(path))
    documents = loader.load()
    source = to_project_relative_source(path)
    for document in documents:
        document.metadata["source"] = source
    return documents
