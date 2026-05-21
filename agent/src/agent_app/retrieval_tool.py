from typing import Any

from rag_app.services.ask_service import ask_question


def run_retrieval_tool(question: str) -> dict[str, Any]:
    return ask_question(question)
