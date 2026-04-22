from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from app.routers import ask as ask_router


def test_ask_returns_answer_and_sources(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    expected = {
        "answer": "LangChain 是一个用于构建 LLM 应用的框架。",
        "sources": [
            {
                "source": "data/raw/langchain-docs.md",
                "section_path": "Introduction > Overview",
                "snippet": "LangChain is a framework for developing applications.",
            }
        ],
    }

    mock_ask_question = Mock(return_value=expected)
    monkeypatch.setattr(ask_router, "ask_question", mock_ask_question)

    response = client.post("/ask", json={"question": "LangChain 是什么？"})

    assert response.status_code == 200
    assert response.json() == expected
    mock_ask_question.assert_called_once_with("LangChain 是什么？")
def test_ask_returns_422_when_question_is_missing(client: TestClient) -> None:

    response = client.post("/ask", json={})

    assert response.status_code == 422