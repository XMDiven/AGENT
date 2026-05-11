from unittest.mock import Mock

from langchain_core.documents import Document

from rag_app.services.ask_service import ask_question

from rag_app.config import config


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
        "retrieval",
        "generation",
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
                },
            },
            {
                "step": "retrieval",
                "status": "completed",
                "detail": {"document_count": 0},
            },
        ],
    }
    mock_retriever.invoke.assert_called_once_with("一个文档里完全没有的问题")
