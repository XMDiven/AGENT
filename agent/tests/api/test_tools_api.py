from fastapi.testclient import TestClient

from agent_app.app.main import app

client = TestClient(app)


def test_list_agent_tools_endpoint_returns_tool_contracts() -> None:
    response = client.get("/agent/tools")

    assert response.status_code == 200

    data = response.json()

    assert [tool["name"] for tool in data] == [
        "retrieval_tool",
        "summary_tool",
        "question_decompose_tool",
        "fallback_tool",
    ]

    retrieval_tool = data[0]

    assert retrieval_tool["description"] == (
        "Retrieve relevant documents from the RAG knowledge base."
    )
    assert retrieval_tool["input_schema"]["required"] == ["question"]
    assert retrieval_tool["input_schema"]["properties"]["question"][
        "type"
    ] == "string"
    assert retrieval_tool["output_schema"]["required"] == [
        "answer",
        "sources",
    ]
    assert retrieval_tool["output_schema"]["properties"]["answer"][
        "type"
    ] == "string"
