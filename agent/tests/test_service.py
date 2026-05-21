from agent_app.service import run_agent


def test_run_agent_uses_retrieval_tool(monkeypatch) -> None:
    expected = {
        "answer": "RAG answer",
        "sources": [],
        "trace": [],
    }

    monkeypatch.setattr(
        "agent_app.executor.run_retrieval_tool",
        lambda question: expected,
    )

    result = run_agent("What is RAG?", needs_retrieval=True)

    assert result.plan.tool.name == "retrieval_tool"
    assert result.tool_result.tool_name == "retrieval_tool"
    assert result.tool_result.status == "success"
    assert result.tool_result.output == expected


def test_run_agent_uses_fallback_tool_when_retrieval_is_not_needed() -> None:
    result = run_agent("hello", needs_retrieval=False)

    assert result.plan.tool.name == "fallback_tool"
    assert result.tool_result.tool_name == "fallback_tool"
    assert result.tool_result.status == "success"
    assert result.tool_result.output == {
        "answer": "No retrieval is needed for this question.",
        "sources": [],
    }
