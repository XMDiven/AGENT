from langchain_core.documents import Document
from rag_app.scripts.evaluate_retrieval import get_sources, has_expected_sources


def test_get_sources_extracts_document_source_metadata() -> None:
    documents = [
        Document(
            page_content="Qdrant is a vector database.",
            metadata={"source": "data/raw/qdrant-docs.md"},
        )
    ]

    assert get_sources(documents) == ["data/raw/qdrant-docs.md"]


def test_has_expected_sources_matches_expected_label_inside_source_path() -> None:
    sources = [
        "/Users/mdiven/Code/Projects/RAG/data/raw/gpt4_technical_report.pdf",
        "/Users/mdiven/Code/Projects/RAG/data/raw/qdrant-docs.md",
    ]

    assert has_expected_sources(
        sources=sources,
        expected_source_contains=["qdrant-docs.md"],
    )

def test_has_expected_sources_returns_false_when_expected_label_is_missing() -> None:
    sources = [
        "/Users/mdiven/Code/Projects/RAG/data/raw/langchain-docs.md",
    ]

    assert not has_expected_sources(
        sources=sources,
        expected_source_contains=["qdrant-docs.md"],
    )
