from unittest.mock import Mock

from langchain_core.documents import Document

from rag_app.config import config
from rag_app.services.ask_service import ask_question


def test_ask_question_plans_comparison_retrieval(monkeypatch) -> None:
    documents = [
        Document(
            page_content="LangChain is used for building LLM applications.",
            metadata={
                "source": "data/raw/langchain-docs.md",
                "section_path": "Overview",
            },
        )
    ]

    mock_retriever = Mock()
    mock_retriever.invoke.return_value = documents

    monkeypatch.setattr(
        "rag_app.services.ask_service.get_retriever",
        lambda: mock_retriever,
    )
    monkeypatch.setattr(
        "rag_app.services.ask_service.format_context",
        lambda docs: "formatted context",
    )
    monkeypatch.setattr(
        "rag_app.services.ask_service.get_client",
        lambda: "fake-llm",
    )
    monkeypatch.setattr(
        "rag_app.services.ask_service.get_qa_prompt",
        lambda: "fake-prompt",
    )
    monkeypatch.setattr(
        "rag_app.services.ask_service.generate_answer",
        lambda question, context, prompt, llm: "LangChain 和 LlamaIndex 适合不同场景。",
    )

    result = ask_question("LangChain 和 LlamaIndex 分别适合做什么？")

    assert result["trace"][1]["detail"] == {
        "question_type": "comparison",
        "retrieval_strategy": "comparison_retrieval",
        "reason": "comparison questions may need evidence from multiple sources",
    }


def test_ask_question_returns_answer_and_sources(monkeypatch) -> None:
    documents = [
        Document(
            page_content="LangChain is a framework for developing applications.",
            metadata={
                "source": "data/raw/langchain-docs.md",
                "section_path": "Introduction > Overview",
            },
        )
    ]

    mock_retriever = Mock()
    mock_retriever.invoke.return_value = documents

    monkeypatch.setattr(
        "rag_app.services.ask_service.get_retriever",
        lambda: mock_retriever,
    )
    monkeypatch.setattr(
        "rag_app.services.ask_service.format_context",
        lambda docs: "formatted context",
    )
    monkeypatch.setattr(
        "rag_app.services.ask_service.get_client",
        lambda: "fake-llm",
    )
    monkeypatch.setattr(
        "rag_app.services.ask_service.get_qa_prompt",
        lambda: "fake-prompt",
    )
    monkeypatch.setattr(
        "rag_app.services.ask_service.generate_answer",
        lambda question, context, prompt, llm: "LangChain 是一个用于构建 LLM 应用的框架。",
    )

    result = ask_question("LangChain 是什么？")

    assert result["answer"] == "LangChain 是一个用于构建 LLM 应用的框架。"
    assert result["sources"] == [
        {
            "source": "data/raw/langchain-docs.md",
            "section_path": "Introduction > Overview",
            "snippet": "LangChain is a framework for developing applications.",
        }
    ]
    assert [item["step"] for item in result["trace"]] == [
        "query_analysis",
        "retrieval_planning",
        "retrieval",
        "generate_answer",
    ]
    assert result["trace"][2]["detail"]["retrieved_sources"] == [
        "data/raw/langchain-docs.md"
    ]
    mock_retriever.invoke.assert_called_once_with("LangChain 是什么？")


def test_ask_question_returns_fallback_when_no_documents(monkeypatch) -> None:
    mock_retriever = Mock()
    mock_retriever.invoke.return_value = []

    monkeypatch.setattr(
        "rag_app.services.ask_service.get_retriever",
        lambda: mock_retriever,
    )

    result = ask_question("一个文档里完全没有的问题")

    assert result == {
        "answer": config.FALLBACK_ANSWER,
        "sources": [],
        "trace": [
            {
                "step": "query_analysis",
                "status": "completed",
                "detail": {
                    "normalized_question": "一个文档里完全没有的问题",
                    "needs_retrieval": True,
                    "reason": "normal knowledge question, use retrieval",
                    "question_type": "general",
                },
            },
            {
                "step": "retrieval_planning",
                "status": "completed",
                "detail": {
                    "question_type": "general",
                    "retrieval_strategy": "standard_retrieval",
                    "reason": "general knowledge questions use standard retrieval",
                },
            },
            {
                "step": "retrieval",
                "status": "completed",
                "detail": {
                    "top_k": config.RETRIEVAL_TOP_K,
                    "document_count": 0,
                    "retrieved_sources": [],
                },
            },
        ],
    }
    mock_retriever.invoke.assert_called_once_with("一个文档里完全没有的问题")


def test_ask_question_skips_retrieval_when_question_is_empty(monkeypatch) -> None:
    mock_retriever = Mock()

    monkeypatch.setattr(
        "rag_app.services.ask_service.get_retriever",
        lambda: mock_retriever,
    )

    result = ask_question("   ")

    assert result == {
        "answer": config.FALLBACK_ANSWER,
        "sources": [],
        "trace": [
            {
                "step": "query_analysis",
                "status": "completed",
                "detail": {
                    "normalized_question": "",
                    "needs_retrieval": False,
                    "reason": "empty question",
                    "question_type": "empty",
                },
            },
            {
                "step": "retrieval_planning",
                "status": "completed",
                "detail": {
                    "question_type": "empty",
                    "retrieval_strategy": "skip_retrieval",
                    "reason": "empty questions do not need retrieval",
                },
            },
            {
                "step": "retrieval",
                "status": "skipped",
                "detail": {
                    "reason": "empty question",
                },
            },
        ],
    }
    mock_retriever.invoke.assert_not_called()
