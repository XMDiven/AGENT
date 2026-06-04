from pathlib import Path
from unittest.mock import Mock

import pytest
from langchain_core.documents import Document

from rag_app.infrastructure.resources import AppResources
from rag_app.services import ingest_service
from rag_app.services.ingest_service import ingest_markdown_file


def test_ingest_markdown_file_returns_counts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
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
        "rag_app.services.ingest_service.load_markdown",
        mock_load_markdown,
    )
    monkeypatch.setattr(
        "rag_app.services.ingest_service.chunk_markdown",
        mock_chunk_markdown,
    )
    monkeypatch.setattr(
        "rag_app.services.ingest_service.ingest_chunks",
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


def test_ingest_markdown_file_uses_resources_vector_store(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
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
        )
    ]
    mock_vector_store = Mock()
    resources = AppResources(
        llm_client=Mock(),
        vector_store=mock_vector_store,
    )
    mock_ingest_chunks = Mock(return_value=["chunk-1"])

    monkeypatch.setattr(
        "rag_app.services.ingest_service.load_markdown",
        Mock(return_value=documents),
    )
    monkeypatch.setattr(
        "rag_app.services.ingest_service.chunk_markdown",
        Mock(return_value=chunks),
    )
    monkeypatch.setattr(
        "rag_app.services.ingest_service.ingest_chunks",
        mock_ingest_chunks,
    )

    result = ingest_markdown_file(
        "data/raw/langchain-docs.md",
        resources=resources,
    )

    assert result["stored_count"] == 1
    mock_ingest_chunks.assert_called_once_with(
        chunks=chunks,
        vector_store=mock_vector_store,
    )


def test_ingest_pdf_file_returns_counts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    documents = [
        Document(
            page_content="RAG systems combine retrieval and generation.",
            metadata={
                "source": "data/raw/rag-paper.pdf",
                "page": 1,
            },
        )
    ]
    chunks = [
        Document(
            page_content="RAG systems combine retrieval and generation.",
            metadata={
                "source": "data/raw/rag-paper.pdf",
                "page": 1,
                "section_path": "page_1",
            },
        )
    ]

    mock_load_pdf = Mock(return_value=documents)
    mock_chunk_pdf = Mock(return_value=chunks)
    mock_ingest_chunks = Mock(return_value=["chunk-1"])

    monkeypatch.setattr(
        ingest_service,
        "load_pdf",
        mock_load_pdf,
        raising=False,
    )
    monkeypatch.setattr(
        ingest_service,
        "chunk_pdf",
        mock_chunk_pdf,
        raising=False,
    )
    monkeypatch.setattr(
        ingest_service,
        "ingest_chunks",
        mock_ingest_chunks,
    )

    result = ingest_service.ingest_pdf_file("data/raw/rag-paper.pdf")

    assert result == {
        "path": "data/raw/rag-paper.pdf",
        "document_count": 1,
        "chunk_count": 1,
        "stored_count": 1,
    }
    mock_load_pdf.assert_called_once_with("data/raw/rag-paper.pdf")
    mock_chunk_pdf.assert_called_once_with(documents)
    mock_ingest_chunks.assert_called_once_with(chunks)


def test_ingest_pdf_file_uses_real_loader_and_chunker(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    pdf_path = tmp_path / "sample.pdf"
    pdf_path.write_bytes(
        b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 144] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>
endobj
4 0 obj
<< /Length 44 >>
stream
BT
/F1 24 Tf
72 72 Td
(Hello PDF) Tj
ET
endstream
endobj
5 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj
xref
0 6
0000000000 65535 f
0000000010 00000 n
0000000062 00000 n
0000000114 00000 n
0000000241 00000 n
0000000335 00000 n
trailer
<< /Root 1 0 R /Size 6 >>
startxref
405
%%EOF
"""
    )

    captured_chunks: list[Document] = []

    def fake_ingest_chunks(chunks: list[Document]) -> list[str]:
        captured_chunks.extend(chunks)
        return ["chunk-1" for _ in chunks]

    monkeypatch.setattr(
        ingest_service,
        "ingest_chunks",
        fake_ingest_chunks,
    )

    result = ingest_service.ingest_pdf_file(str(pdf_path))

    assert result == {
        "path": str(pdf_path),
        "document_count": 1,
        "chunk_count": 1,
        "stored_count": 1,
    }
    assert "Hello PDF" in captured_chunks[0].page_content
    assert captured_chunks[0].metadata["source"] == str(pdf_path)
    assert captured_chunks[0].metadata["page"] == 0
    assert captured_chunks[0].metadata["doc_type"] == "pdf"
    assert captured_chunks[0].metadata["section_path"] == "page_1"


def test_ingest_file_dispatches_markdown(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    expected_result = {
        "path": "data/raw/example.md",
        "document_count": 1,
        "chunk_count": 2,
        "stored_count": 2,
    }
    mock_ingest_markdown_file = Mock(return_value=expected_result)

    monkeypatch.setattr(
        ingest_service,
        "ingest_markdown_file",
        mock_ingest_markdown_file,
    )

    result = ingest_service.ingest_file("data/raw/example.md")

    assert result == expected_result
    mock_ingest_markdown_file.assert_called_once_with("data/raw/example.md")


def test_ingest_file_dispatches_pdf(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    expected_result = {
        "path": "data/raw/example.pdf",
        "document_count": 1,
        "chunk_count": 3,
        "stored_count": 3,
    }
    mock_ingest_pdf_file = Mock(return_value=expected_result)

    monkeypatch.setattr(
        ingest_service,
        "ingest_pdf_file",
        mock_ingest_pdf_file,
    )

    result = ingest_service.ingest_file("data/raw/example.pdf")

    assert result == expected_result
    mock_ingest_pdf_file.assert_called_once_with("data/raw/example.pdf")


def test_ingest_file_rejects_unsupported_file_type() -> None:
    with pytest.raises(ValueError, match="Unsupported file type: .txt"):
        ingest_service.ingest_file("data/raw/example.txt")
