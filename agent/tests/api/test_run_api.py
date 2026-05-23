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

    assert data["plan"]["tool"]["name"] == "fallback_tool"
    assert data["tool_result"]["tool_name"] == "fallback_tool"
    assert data["tool_result"]["status"] == "success"
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

    assert data["plan"]["tool"]["name"] == "retrieval_tool"
    assert data["tool_result"] == {
        "tool_name": "retrieval_tool",
        "status": "success",
        "output": expected,
        "attempts": [
            {
                "attempt": 1,
                "status": "success",
            }
        ],
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


def test_run_agent_endpoint_uses_summary_tool_for_summary_question() -> None:
    response = client.post(
        "/agent/run",
        json={
            "question": "请总结 LangChain 的用途",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["plan"]["tool"]["name"] == "summary_tool"
    assert data["tool_result"] == {
        "tool_name": "summary_tool",
        "status": "success",
        "output": {
            "summary": "请总结 LangChain 的用途",
        },
        "attempts": [
            {
                "attempt": 1,
                "status": "success",
            }
        ],
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

    assert data["tool_result"] == {
        "tool_name": "retrieval_tool",
        "status": "failed",
        "output": {
            "error_type": "RuntimeError",
            "error": "rag unavailable",
        },
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
