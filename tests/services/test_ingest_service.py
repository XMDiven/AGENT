from unittest.mock import Mock

from langchain_core.documents import Document

from src.services.ingest_service import ingest_markdown_file


def test_ingest_markdown_file_returns_counts(monkeypatch) -> None:
    documents = [
        Document(
            page_content="# LangChain\nLangChain is a framework.",
            metadata={"source": "data/raw/langchain-docs.md"},
        )
    ]
    chunks = [
        Document(
            page_content="LangChain is a framework.",
            metadata={
                "source": "data/raw/langchain-docs.md",
                "section_path": "LangChain",
            },
        ),
        Document(
            page_content="It helps build LLM applications.",
            metadata={
                "source": "data/raw/langchain-docs.md",
                "section_path": "LangChain",
            },
        ),
    ]

    mock_load_markdown = Mock(return_value=documents)
    mock_chunk_markdown = Mock(return_value=chunks)
    mock_ingest_chunks = Mock(return_value=["chunk-1", "chunk-2"])

    monkeypatch.setattr(
        "src.services.ingest_service.load_markdown",
        mock_load_markdown,
    )
    monkeypatch.setattr(
        "src.services.ingest_service.chunk_markdown",
        mock_chunk_markdown,
    )
    monkeypatch.setattr(
        "src.services.ingest_service.ingest_chunks",
        mock_ingest_chunks,
    )

    result = ingest_markdown_file("data/raw/langchain-docs.md")

    assert result == {
        "path": "data/raw/langchain-docs.md",
        "document_count": 1,
        "chunk_count": 2,
        "stored_count": 2,
    }
    mock_load_markdown.assert_called_once_with("data/raw/langchain-docs.md")
    mock_chunk_markdown.assert_called_once_with(documents)
    mock_ingest_chunks.assert_called_once_with(chunks)
