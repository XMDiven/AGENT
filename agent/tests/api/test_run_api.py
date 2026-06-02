from fastapi.testclient import TestClient

from agent_app.app.main import app

client = TestClient(app)


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


def test_run_agent_endpoint_uses_summary_tool_for_summary_question() -> None:
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


def test_run_agent_endpoint_uses_question_decompose_tool_for_comparison_question() -> None:
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
    assert data["answer"] == ""
    assert data["sources"] == []
    assert data["selected_tool"] == "question_decompose_tool"
    assert data["tool_status"] == "success"
    assert data["tool_output"] == {
        "sub_questions": [
            "LangChain 适合做什么？",
            "LlamaIndex 适合做什么？",
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
                {
                    "attempt": 2,
                    "status": "failed",
                    "error_type": "RuntimeError",
                    "error": "rag unavailable",
                },
                {
                    "attempt": 3,
                    "status": "failed",
                    "error_type": "RuntimeError",
                    "error": "rag unavailable",
                },
            ],
        },
    }
