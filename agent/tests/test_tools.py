import pytest

from agent_app.tools.registry import get_tool, list_tools


def test_list_tools_returns_registered_tools() -> None:
    tools = list_tools()

    assert [tool.name for tool in tools] == [
        "retrieval_tool",
        "summary_tool",
        "question_decompose_tool",
        "fallback_tool",
    ]


def test_get_tool_returns_registered_tool() -> None:
    tool = get_tool("retrieval_tool")

    assert tool.name == "retrieval_tool"
    assert (
        tool.description
        == "Retrieve relevant documents from the RAG knowledge base."
    )


def test_get_tool_returns_tool_contract() -> None:
    tool = get_tool("retrieval_tool")

    assert tool.input_schema["type"] == "object"
    assert tool.input_schema["required"] == ["question"]
    assert tool.input_schema["properties"]["question"]["type"] == "string"
    assert tool.output_schema["type"] == "object"
    assert tool.output_schema["required"] == ["answer", "sources"]
    assert tool.output_schema["properties"]["answer"]["type"] == "string"


def test_all_tools_have_input_and_output_schemas() -> None:
    for tool in list_tools():
        assert tool.input_schema["type"] == "object"
        assert tool.output_schema["type"] == "object"
        assert "properties" in tool.input_schema
        assert "properties" in tool.output_schema


def test_get_tool_raises_for_unknown_tool() -> None:
    with pytest.raises(ValueError, match="Unknown tool: unknown_tool"):
        get_tool("unknown_tool")
