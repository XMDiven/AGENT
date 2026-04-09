from unittest import TestCase
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from config import config
from src.services import ask_service

client = TestClient(app)


class HealthApiTest(TestCase):
    def test_health_returns_ok(self) -> None:
        response = client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})


class AskApiTest(TestCase):
    @patch("app.routers.ask.ask_question")
    def test_ask_returns_answer_and_sources(self, mock_ask_question) -> None:
        mock_ask_question.return_value = {
            "answer": "LangChain 是一个用于构建 LLM 应用的框架。",
            "sources": [
                {
                    "source": "data/raw/langchain-docs.md",
                    "section_path": "Introduction > Overview",
                    "snippet": "LangChain is a framework for developing applications.",
                }
            ],
        }

        response = client.post(
            "/ask",
            json={"question": "LangChain 是什么？"},
        )

        self.assertEqual(response.status_code, 200)

        body = response.json()
        self.assertIn("answer", body)
        self.assertIn("sources", body)
        self.assertEqual(
            body["answer"],
            "LangChain 是一个用于构建 LLM 应用的框架。",
        )
        self.assertEqual(len(body["sources"]), 1)
        self.assertEqual(
            body["sources"][0]["source"],
            "data/raw/langchain-docs.md",
        )

    def test_ask_returns_422_when_question_is_missing(self) -> None:
        response = client.post("/ask", json={})

        self.assertEqual(response.status_code, 422)


class AskServiceTest(TestCase):
    @patch("src.services.ask_service.get_retriever")
    def test_ask_question_returns_fallback_when_no_documents(
        self,
        mock_get_retriever,
    ) -> None:
        class EmptyRetriever:
            def invoke(self, question: str) -> list[object]:
                return []

        mock_get_retriever.return_value = EmptyRetriever()

        result = ask_service.ask_question("out of scope question")

        self.assertEqual(result["answer"], config.FALLBACK_ANSWER)
        self.assertEqual(result["sources"], [])
