from typing import Any

from fastapi.testclient import TestClient

from agent_app.app.main import app
from agent_app.orchestration.tool_selector import ToolSelection
from agent_app.tools import get_tool

client = TestClient(app)


def patch_tool_selection(
    monkeypatch,
    tool_name: str,
    tool_args: dict[str, Any],
    reason: str = "llm selected tool via native tool calling",
) -> None:
    monkeypatch.setattr(
        "agent_app.orchestration.planner.select_tool_with_llm",
        lambda question: ToolSelection(
            tool=get_tool(tool_name),
            tool_args=tool_args,
            reason=reason,
        ),
    )


def test_run_agent_endpoint_uses_fallback_tool_for_empty_question() -> None:
    response = client.post(
        "/agent/run",
        json={
            "question": "",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "plan" not in data
    assert "tool_result" not in data
    assert data["answer"] == "No retrieval is needed for this question."
    assert data["sources"] == []
    assert data["selected_tool"] == "fallback_tool"
    assert data["tool_status"] == "success"
    assert data["tool_output"] == {
        "answer": "No retrieval is needed for this question.",
        "sources": [],
    }
    assert data["trace"] == [
        {
            "step": "analyze_question",
            "status": "completed",
            "detail": {
                "needs_retrieval": False,
                "question_type": "empty",
                "reason": "empty question",
            },
        },
        {
            "step": "plan_tool",
            "status": "completed",
            "detail": {
                "tool_name": "fallback_tool",
                "reason": "question does not require retrieval",
            },
        },
        {
            "step": "execute_tool",
            "status": "success",
            "detail": {
                "tool_name": "fallback_tool",
                "attempts": [
                    {
                        "attempt": 1,
                        "status": "success",
                    }
                ],
            },
        },
    ]


def test_run_agent_endpoint_returns_success_when_retrieval_succeeds(
    monkeypatch,
) -> None:
    patch_tool_selection(
        monkeypatch=monkeypatch,
        tool_name="retrieval_tool",
        tool_args={"question": "What is RAG?"},
    )

    expected = {
        "answer": "RAG answer",
        "sources": [],
        "trace": [],
    }

    monkeypatch.setattr(
        "agent_app.orchestration.executor.run_retrieval_tool",
        lambda question: expected,
    )

    response = client.post(
        "/agent/run",
        json={
            "question": "What is RAG?",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "plan" not in data
    assert "tool_result" not in data
    assert data["answer"] == "RAG answer"
    assert data["sources"] == []
    assert data["selected_tool"] == "retrieval_tool"
    assert data["tool_status"] == "success"
    assert data["tool_output"] == expected
    assert data["trace"][1]["detail"]["tool_args"] == {
        "question": "What is RAG?",
    }
    assert data["trace"][-1] == {
        "step": "execute_tool",
        "status": "success",
        "detail": {
            "tool_name": "retrieval_tool",
            "attempts": [
                {
                    "attempt": 1,
                    "status": "success",
                }
            ],
        },
    }


def test_run_agent_endpoint_uses_summary_tool_for_summary_question(
    monkeypatch,
) -> None:
    patch_tool_selection(
        monkeypatch=monkeypatch,
        tool_name="summary_tool",
        tool_args={"text": "请总结 LangChain 的用途"},
    )

    response = client.post(
        "/agent/run",
        json={
            "question": "请总结 LangChain 的用途",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "plan" not in data
    assert "tool_result" not in data
    assert data["answer"] == "请总结 LangChain 的用途"
    assert data["sources"] == []
    assert data["selected_tool"] == "summary_tool"
    assert data["tool_status"] == "success"
    assert data["tool_output"] == {
        "summary": "请总结 LangChain 的用途",
    }
    assert data["trace"][1]["detail"]["tool_args"] == {
        "text": "请总结 LangChain 的用途",
    }
    assert data["trace"][-1] == {
        "step": "execute_tool",
        "status": "success",
        "detail": {
            "tool_name": "summary_tool",
            "attempts": [
                {
                    "attempt": 1,
                    "status": "success",
                }
            ],
        },
    }


def test_run_agent_endpoint_uses_question_decompose_tool_for_comparison_question(
    monkeypatch,
) -> None:
    patch_tool_selection(
        monkeypatch=monkeypatch,
        tool_name="question_decompose_tool",
        tool_args={"question": "LangChain 和 LlamaIndex 分别适合做什么？"},
    )

    def fake_retrieval_tool(question: str) -> dict:
        return {
            "answer": f"{question} answer",
            "sources": [],
            "trace": [],
        }

    monkeypatch.setattr(
        "agent_app.orchestration.executor.run_retrieval_tool",
        fake_retrieval_tool,
    )

    response = client.post(
        "/agent/run",
        json={
            "question": "LangChain 和 LlamaIndex 分别适合做什么？",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "plan" not in data
    assert "tool_result" not in data
    assert data["answer"] == (
        "1. LangChain 适合做什么？\n"
        "LangChain 适合做什么？ answer\n\n"
        "2. LlamaIndex 适合做什么？\n"
        "LlamaIndex 适合做什么？ answer"
    )
    assert data["sources"] == []
    assert data["selected_tool"] == "question_decompose_tool"
    assert data["tool_status"] == "success"
    assert data["tool_output"] == {
        "answer": (
            "1. LangChain 适合做什么？\n"
            "LangChain 适合做什么？ answer\n\n"
            "2. LlamaIndex 适合做什么？\n"
            "LlamaIndex 适合做什么？ answer"
        ),
        "sources": [],
        "sub_questions": [
            "LangChain 适合做什么？",
            "LlamaIndex 适合做什么？",
        ],
        "sub_results": [
            {
                "question": "LangChain 适合做什么？",
                "status": "success",
                "answer": "LangChain 适合做什么？ answer",
                "sources": [],
                "attempts": [
                    {
                        "attempt": 1,
                        "status": "success",
                    }
                ],
            },
            {
                "question": "LlamaIndex 适合做什么？",
                "status": "success",
                "answer": "LlamaIndex 适合做什么？ answer",
                "sources": [],
                "attempts": [
                    {
                        "attempt": 1,
                        "status": "success",
                    }
                ],
            },
        ],
        "reason": "question contains explicit multi-part intent",
        "decomposition_strategy": "comparison",
    }
    assert data["trace"][-1] == {
        "step": "execute_tool",
        "status": "success",
        "detail": {
            "tool_name": "question_decompose_tool",
            "attempts": [
                {
                    "attempt": 1,
                    "status": "success",
                }
            ],
            "decomposition_strategy": "comparison",
            "sub_question_count": 2,
        },
    }


def test_run_agent_endpoint_returns_failed_tool_result_when_retrieval_fails(
    monkeypatch,
) -> None:
    patch_tool_selection(
        monkeypatch=monkeypatch,
        tool_name="retrieval_tool",
        tool_args={"question": "What is RAG?"},
    )

    def raise_error(question: str) -> None:
        raise RuntimeError("rag unavailable")

    monkeypatch.setattr(
        "agent_app.orchestration.executor.run_retrieval_tool",
        raise_error,
    )

    response = client.post(
        "/agent/run",
        json={
            "question": "What is RAG?",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "plan" not in data
    assert "tool_result" not in data
    assert data["answer"] == "rag unavailable"
    assert data["sources"] == []
    assert data["selected_tool"] == "retrieval_tool"
    assert data["tool_status"] == "failed"
    assert data["tool_output"] == {
        "error_type": "RuntimeError",
        "error": "rag unavailable",
    }
    assert data["trace"][-1] == {
        "step": "execute_tool",
        "status": "failed",
        "detail": {
            "tool_name": "retrieval_tool",
            "attempts": [
                {
                    "attempt": 1,
                    "status": "failed",
                    "error_type": "RuntimeError",
                    "error": "rag unavailable",
                },
            ],
        },
    }
