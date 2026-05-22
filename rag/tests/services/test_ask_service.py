from unittest.mock import Mock

from langchain_core.documents import Document

from rag_app.config import config
from rag_app.services.ask_service import (
    apply_retrieval_strategy,
    ask_question,
    stream_ask_question,
)


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
        lambda top_k=None: mock_retriever,
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
        "retrieval_query": "LangChain 和 LlamaIndex 分别适合做什么？",
        "top_k": config.RETRIEVAL_TOP_K,
        "reason": "comparison questions may need evidence from multiple sources",
    }
    assert result["trace"][2]["detail"]["retrieval_strategy"] == (
        "comparison_retrieval"
    )


def test_apply_comparison_retrieval_interleaves_documents_by_source() -> None:
    documents = [
        Document(page_content="A1", metadata={"source": "source-a.md"}),
        Document(page_content="A2", metadata={"source": "source-a.md"}),
        Document(page_content="B1", metadata={"source": "source-b.md"}),
        Document(page_content="C1", metadata={"source": "source-c.md"}),
    ]

    result = apply_retrieval_strategy(
        documents=documents,
        retrieval_strategy="comparison_retrieval",
    )

    assert [document.page_content for document in result] == [
        "A1",
        "B1",
        "C1",
        "A2",
    ]


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
        lambda top_k=None: mock_retriever,
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


def test_ask_question_returns_fallback_when_answer_generation_fails(
    monkeypatch,
) -> None:
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
        lambda top_k=None: mock_retriever,
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

    def raise_generation_error(question, context, prompt, llm):
        raise RuntimeError("LLM unavailable")

    monkeypatch.setattr(
        "rag_app.services.ask_service.generate_answer",
        raise_generation_error,
    )

    result = ask_question("LangChain 是什么？")

    assert result["answer"] == config.FALLBACK_ANSWER
    assert result["sources"] == [
        {
            "source": "data/raw/langchain-docs.md",
            "section_path": "Introduction > Overview",
            "snippet": "LangChain is a framework for developing applications.",
        }
    ]
    assert result["trace"][-1] == {
        "step": "generate_answer",
        "status": "failed",
        "detail": {
            "attempts": config.MAX_GENERATION_RETRY + 1,
            "error_type": "RuntimeError",
        },
    }
    mock_retriever.invoke.assert_called_once_with("LangChain 是什么？")


def test_ask_question_retries_answer_generation_once(monkeypatch) -> None:
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
    mock_generate_answer = Mock(
        side_effect=[
            RuntimeError("temporary LLM failure"),
            "LangChain 是一个用于构建 LLM 应用的框架。",
        ]
    )

    monkeypatch.setattr(
        "rag_app.services.ask_service.get_retriever",
        lambda top_k=None: mock_retriever,
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
        mock_generate_answer,
    )

    result = ask_question("LangChain 是什么？")

    assert result["answer"] == "LangChain 是一个用于构建 LLM 应用的框架。"
    assert mock_generate_answer.call_count == 2
    assert result["trace"][-2] == {
        "step": "generate_answer",
        "status": "retrying",
        "detail": {
            "attempt": 1,
            "error_type": "RuntimeError",
        },
    }
    assert result["trace"][-1] == {
        "step": "generate_answer",
        "status": "completed",
        "detail": {
            "attempt": 2,
        },
    }


def test_ask_question_returns_fallback_when_no_documents(monkeypatch) -> None:
    mock_retriever = Mock()
    mock_retriever.invoke.return_value = []

    monkeypatch.setattr(
        "rag_app.services.ask_service.get_retriever",
        lambda top_k=None: mock_retriever,
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
                    "retrieval_query": "一个文档里完全没有的问题",
                    "top_k": config.RETRIEVAL_TOP_K,
                    "reason": "general knowledge questions use standard retrieval",
                },
            },
            {
                "step": "retrieval",
                "status": "completed",
                "detail": {
                    "retrieval_strategy": "standard_retrieval",
                    "retrieval_query": "一个文档里完全没有的问题",
                    "top_k": config.RETRIEVAL_TOP_K,
                    "document_count": 0,
                    "retrieved_sources": [],
                },
            },
        ],
    }
    mock_retriever.invoke.assert_called_once_with("一个文档里完全没有的问题")


def test_stream_ask_question_streams_answer_chunks(monkeypatch) -> None:
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
    mock_stream_answer = Mock(return_value=iter(["LangChain 是", "一个框架。"]))

    monkeypatch.setattr(
        "rag_app.services.ask_service.get_retriever",
        lambda top_k=None: mock_retriever,
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
        "rag_app.services.ask_service.stream_answer",
        mock_stream_answer,
    )

    events = list(stream_ask_question("LangChain 是什么？"))

    assert events[:2] == [
        {
            "type": "answer_delta",
            "content": "LangChain 是",
        },
        {
            "type": "answer_delta",
            "content": "一个框架。",
        },
    ]
    assert events[-3:] == [
        {
            "type": "sources",
            "sources": [
                {
                    "source": "data/raw/langchain-docs.md",
                    "section_path": "Introduction > Overview",
                    "snippet": "LangChain is a framework for developing applications.",
                }
            ],
        },
        {
            "type": "trace",
            "trace": [
                {
                    "step": "query_analysis",
                    "status": "completed",
                    "detail": {
                        "normalized_question": "LangChain 是什么？",
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
                        "retrieval_query": "LangChain 是什么？",
                        "top_k": config.RETRIEVAL_TOP_K,
                        "reason": "general knowledge questions use standard retrieval",
                    },
                },
                {
                    "step": "retrieval",
                    "status": "completed",
                    "detail": {
                        "retrieval_strategy": "standard_retrieval",
                        "retrieval_query": "LangChain 是什么？",
                        "top_k": config.RETRIEVAL_TOP_K,
                        "document_count": 1,
                        "retrieved_sources": ["data/raw/langchain-docs.md"],
                    },
                },
                {
                    "step": "generate_answer",
                    "status": "completed",
                    "detail": {"streaming": True},
                },
            ],
        },
        {
            "type": "done",
        },
    ]
    mock_stream_answer.assert_called_once_with(
        question="LangChain 是什么？",
        context="formatted context",
        prompt="fake-prompt",
        llm="fake-llm",
    )
    mock_retriever.invoke.assert_called_once_with("LangChain 是什么？")


def test_ask_question_skips_retrieval_when_question_is_empty(monkeypatch) -> None:
    mock_retriever = Mock()

    monkeypatch.setattr(
        "rag_app.services.ask_service.get_retriever",
        lambda top_k=None: mock_retriever,
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
                    "retrieval_query": "",
                    "top_k": 0,
                    "reason": "empty questions do not need retrieval",
                },
            },
            {
                "step": "retrieval",
                "status": "skipped",
                "detail": {
                    "retrieval_strategy": "skip_retrieval",
                    "retrieval_query": "",
                    "top_k": 0,
                    "reason": "empty questions do not need retrieval",
                },
            },
        ],
    }
    mock_retriever.invoke.assert_not_called()
