import pytest
from langchain_core.documents import Document

from rag_app.config import config
from rag_app.scripts.evaluate_retrieval import (
    RetrievalEvalCase,
    count_expected_source_hits,
    evaluate_source_hits,
    find_first_hit_rank,
    get_sources,
    has_expected_sources,
    run_evaluation,
)


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


def test_find_first_hit_rank_returns_first_matching_source_position() -> None:
    sources = [
        "data/raw/llamaindex-docs.md",
        "data/raw/03-langchain-README.md",
    ]

    assert (
        find_first_hit_rank(
            sources=sources,
            expected_source_contains=["langchain"],
        )
        == 2
    )


def test_find_first_hit_rank_returns_none_when_no_source_matches() -> None:
    assert (
        find_first_hit_rank(
            sources=["data/raw/llamaindex-docs.md"],
            expected_source_contains=["qdrant-docs.md"],
        )
        is None
    )


def test_count_expected_source_hits_counts_each_expected_label_once() -> None:
    sources = [
        "data/raw/llamaindex-docs.md",
        "data/raw/llamaindex-docs.md",
        "data/raw/03-langchain-README.md",
    ]

    assert (
        count_expected_source_hits(
            sources=sources,
            expected_source_contains=["langchain", "llamaindex"],
        )
        == 2
    )


def test_has_expected_sources_all_fails_when_one_expected_label_is_missing() -> None:
    assert not has_expected_sources(
        sources=["data/raw/llamaindex-docs.md"],
        expected_source_contains=["langchain", "llamaindex"],
        match="all",
    )


def test_has_expected_sources_raises_for_unsupported_match_mode() -> None:
    with pytest.raises(ValueError, match="Unsupported match mode"):
        has_expected_sources(
            sources=["data/raw/llamaindex-docs.md"],
            expected_source_contains=["llamaindex"],
            match="invalid",
        )


def test_evaluate_source_hits_returns_ranking_and_coverage_metrics() -> None:
    result = evaluate_source_hits(
        sources=[
            "data/raw/llamaindex-docs.md",
            "data/raw/03-langchain-README.md",
        ],
        expected_source_contains=["langchain", "llamaindex"],
        match="all",
    )

    assert result == {
        "passed": True,
        "first_hit_rank": 1,
        "reciprocal_rank": 1.0,
        "expected_source_hit_count": 2,
        "expected_source_total": 2,
        "expected_source_coverage": 1.0,
    }


def test_evaluate_source_hits_returns_zero_metrics_when_no_source_matches() -> None:
    result = evaluate_source_hits(
        sources=["data/raw/langchain-docs.md"],
        expected_source_contains=["qdrant-docs.md"],
    )

    assert result == {
        "passed": False,
        "first_hit_rank": None,
        "reciprocal_rank": 0.0,
        "expected_source_hit_count": 0,
        "expected_source_total": 1,
        "expected_source_coverage": 0.0,
    }


def test_run_evaluation_summarizes_ranking_metrics(monkeypatch) -> None:
    cases = [
        RetrievalEvalCase(
            id="case_1",
            question="Question one",
            expected_source_contains=["qdrant"],
        ),
        RetrievalEvalCase(
            id="case_2",
            question="Question two",
            expected_source_contains=["langchain"],
        ),
    ]

    documents_by_question = {
        "Question one": [
            Document(
                page_content="",
                metadata={"source": "data/raw/qdrant-docs.md"},
            )
        ],
        "Question two": [
            Document(
                page_content="",
                metadata={"source": "data/raw/llamaindex-docs.md"},
            ),
            Document(
                page_content="",
                metadata={"source": "data/raw/03-langchain-README.md"},
            ),
        ],
    }

    class FakeRetriever:
        def invoke(self, question: str) -> list[Document]:
            return documents_by_question[question]

    monkeypatch.setattr(
        "rag_app.scripts.evaluate_retrieval.load_case",
        lambda: cases,
    )
    monkeypatch.setattr(
        "rag_app.scripts.evaluate_retrieval.get_retriever",
        lambda **kwargs: FakeRetriever(),
    )

    summary = run_evaluation()

    assert summary["passed"] == 2
    assert summary["total"] == 2
    assert summary["source_hit_rate"] == 1.0
    assert summary["mrr"] == 0.75
    assert summary["average_expected_source_coverage"] == 1.0
    assert summary["average_unique_source_count"] == 1.5
    assert summary["average_duplicate_source_count"] == 0.0


def test_run_evaluation_passes_retrieval_options_to_retriever(monkeypatch) -> None:
    cases = [
        RetrievalEvalCase(
            id="case_1",
            question="Question one",
            expected_source_contains=["qdrant"],
        ),
    ]
    documents = [
        Document(
            page_content="",
            metadata={"source": "data/raw/qdrant-docs.md"},
        )
    ]
    calls = []

    class FakeRetriever:
        def invoke(self, question: str) -> list[Document]:
            return documents

    def fake_get_retriever(**kwargs) -> FakeRetriever:
        calls.append(kwargs)
        return FakeRetriever()

    monkeypatch.setattr(
        "rag_app.scripts.evaluate_retrieval.load_case",
        lambda: cases,
    )
    monkeypatch.setattr(
        "rag_app.scripts.evaluate_retrieval.get_retriever",
        fake_get_retriever,
    )

    summary = run_evaluation(
        top_k=7,
        search_type="mmr",
        fetch_k=50,
        lambda_mult=0.3,
    )

    assert calls == [
        {
            "top_k": 7,
            "search_type": "mmr",
            "fetch_k": 50,
            "lambda_mult": 0.3,
        }
    ]
    assert summary["retrieval_config"] == {
        "top_k": 7,
        "search_type": "mmr",
        "fetch_k": 50,
        "lambda_mult": 0.3,
    }


def test_run_evaluation_uses_configured_default_retrieval_config(
    monkeypatch,
) -> None:
    monkeypatch.setattr(config, "RETRIEVAL_SEARCH_TYPE", "mmr")
    monkeypatch.setattr(config, "RETRIEVAL_TOP_K", 7)
    monkeypatch.setattr(config, "RETRIEVAL_FETCH_K", 50)
    monkeypatch.setattr(config, "RETRIEVAL_LAMBDA_MULT", 0.3)

    cases = [
        RetrievalEvalCase(
            id="case_1",
            question="Question one",
            expected_source_contains=["qdrant"],
        ),
    ]
    documents = [
        Document(
            page_content="",
            metadata={"source": "data/raw/qdrant-docs.md"},
        )
    ]
    calls = []

    class FakeRetriever:
        def invoke(self, question: str) -> list[Document]:
            return documents

    def fake_get_retriever(**kwargs) -> FakeRetriever:
        calls.append(kwargs)
        return FakeRetriever()

    monkeypatch.setattr(
        "rag_app.scripts.evaluate_retrieval.load_case",
        lambda: cases,
    )
    monkeypatch.setattr(
        "rag_app.scripts.evaluate_retrieval.get_retriever",
        fake_get_retriever,
    )

    summary = run_evaluation()

    assert calls == [
        {
            "top_k": None,
            "search_type": None,
            "fetch_k": None,
            "lambda_mult": None,
        }
    ]
    assert summary["retrieval_config"] == {
        "top_k": config.RETRIEVAL_TOP_K,
        "search_type": "mmr",
        "fetch_k": config.RETRIEVAL_FETCH_K,
        "lambda_mult": config.RETRIEVAL_LAMBDA_MULT,
    }
