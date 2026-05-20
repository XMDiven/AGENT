import pytest

from agent_app.tools import get_tool, list_tools


def test_list_tools_returns_registered_tools() -> None:
    tools = list_tools()

    assert [tool.name for tool in tools] == [
        "retrieval_tool",
        "fallback_tool",
    ]


def test_get_tool_returns_registered_tool() -> None:
    tool = get_tool("retrieval_tool")

    assert tool.name == "retrieval_tool"
    assert (
        tool.description
        == "Retrieve relevant documents from the RAG knowledge base."
    )


def test_get_tool_raises_for_unknown_tool() -> None:
    with pytest.raises(ValueError, match="Unknown tool: unknown_tool"):
        get_tool("unknown_tool")
