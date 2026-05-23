from agent_app.tools.summary import run_summary_tool


def test_run_summary_tool_normalizes_whitespace() -> None:
    result = run_summary_tool("  LangChain   helps build   LLM apps.  ")

    assert result == {
        "summary": "LangChain helps build LLM apps.",
    }


def test_run_summary_tool_returns_fallback_for_empty_text() -> None:
    result = run_summary_tool("   ")

    assert result == {
        "summary": "No text provided for summarization.",
    }


def test_run_summary_tool_truncates_long_text() -> None:
    result = run_summary_tool("abcdef", max_chars=3)

    assert result == {
        "summary": "abc...",
    }
