import pytest
from langchain_core.documents import Document

from config import config
from src.ingestion.chunkers.pdf_chunker import chunk_pdf

def test_pdf_chunker(
        monkeypatch : pytest.MonkeyPatch,
) -> None:
    documents = [
        Document(
            page_content="RAG combines retrieval and generation.",
            metadata={
                "source": "data/raw/rag-paper.pdf",
                "page": 0,
            },
        )
    ]

    monkeypatch.setattr(config ,  "CHUNK_SIZE" , 100)
    monkeypatch.setattr(config ,  "CHUNK_OVERLAP" , 0)

    chunks = chunk_pdf(documents)

    assert len(chunks) == 1
    assert chunks[0].page_content == "RAG combines retrieval and generation."
    assert chunks[0].metadata["source"] == "data/raw/rag-paper.pdf"
    assert chunks[0].metadata["page"] == 0
    assert chunks[0].metadata["doc_type"] == "pdf"
    assert chunks[0].metadata["section_path"] == "page_1"
