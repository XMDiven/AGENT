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
            },
        },
    ]
