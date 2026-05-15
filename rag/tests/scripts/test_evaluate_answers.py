from rag_app.scripts.evaluate_answers import (
    answer_has_forbidden_fragments,
    evaluate_answer_result,
    get_answer_source_paths,
)
from rag_app.config import config
from rag_app.scripts.evaluate_retrieval import RetrievalEvalCase


def test_get_answer_source_paths_extracts_sources_from_answer_result() -> None:
    result = {
        "answer": "Qdrant is used for vector search. [1]",
        "sources": [
            {
                "source": "data/raw/qdrant-docs.md",
                "section_path": "unknown",
                "snippet": "Qdrant is a vector search engine.",
            }
        ],
    }

    assert get_answer_source_paths(result) == ["data/raw/qdrant-docs.md"]


def test_answer_has_forbidden_fragments_detects_source_metadata() -> None:
    answer = "RAG combines retrieval and generation. source:data/raw/rag.pdf"

    assert answer_has_forbidden_fragments(answer)


def test_answer_has_forbidden_fragments_allows_numbered_citations() -> None:
    answer = "RAG combines retrieval and generation. [1]"

    assert not answer_has_forbidden_fragments(answer)


def test_evaluate_answer_result_passes_when_answer_and_sources_are_valid() -> None:
    case = RetrievalEvalCase(
        id="qdrant_usage",
        question="What is Qdrant used for?",
        expected_source_contains=["qdrant-docs.md"],
    )
    result = {
        "answer": "Qdrant is used for vector search. [1]",
        "sources": [
            {
                "source": "data/raw/qdrant-docs.md",
                "section_path": "unknown",
                "snippet": "Qdrant is a vector search engine.",
            }
        ],
    }

    passed, failures = evaluate_answer_result(case, result)

    assert passed
    assert failures == []


def test_evaluate_answer_result_fails_when_expected_source_is_missing() -> None:
    case = RetrievalEvalCase(
        id="qdrant_usage",
        question="What is Qdrant used for?",
        expected_source_contains=["qdrant-docs.md"],
    )
    result = {
        "answer": "Qdrant is used for vector search. [1]",
        "sources": [
            {
                "source": "data/raw/langchain-docs.md",
                "section_path": "unknown",
                "snippet": "LangChain docs.",
            }
        ],
    }

    passed, failures = evaluate_answer_result(case, result)

    assert not passed
    assert "expected source not found" in failures


def test_evaluate_answer_result_fails_when_answer_is_fallback() -> None:
    case = RetrievalEvalCase(
        id="qdrant_usage",
        question="What is Qdrant used for?",
        expected_source_contains=["qdrant-docs.md"],
    )
    result = {
        "answer": config.FALLBACK_ANSWER,
        "sources": [
            {
                "source": "data/raw/qdrant-docs.md",
                "section_path": "unknown",
                "snippet": "Qdrant is a vector search engine.",
            }
        ],
    }

    passed, failures = evaluate_answer_result(case, result)

    assert not passed
    assert "answer is fallback" in failures


def test_evaluate_answer_result_fails_when_generation_trace_failed() -> None:
    case = RetrievalEvalCase(
        id="qdrant_usage",
        question="What is Qdrant used for?",
        expected_source_contains=["qdrant-docs.md"],
    )
    result = {
        "answer": "Qdrant is used for vector search. [1]",
        "sources": [
            {
                "source": "data/raw/qdrant-docs.md",
                "section_path": "unknown",
                "snippet": "Qdrant is a vector search engine.",
            }
        ],
        "trace": [
            {
                "step": "generate_answer",
                "status": "failed",
                "detail": {
                    "attempts": 2,
                    "error_type": "RateLimitError",
                },
            }
        ],
    }

    passed, failures = evaluate_answer_result(case, result)

    assert not passed
    assert "answer generation failed" in failures
