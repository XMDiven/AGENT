from pathlib import Path

from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_core.documents import Document


def load_markdown(path: str | Path) -> list[Document]:

    loader = UnstructuredMarkdownLoader(str(path))
    return loader.load()
