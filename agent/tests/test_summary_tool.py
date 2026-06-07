from dataclasses import dataclass

from agent_app.tools.summary import run_summary_tool


@dataclass(frozen=True)
class FakeMessage:
    content: str


class FakeLLM:
    def __init__(self, content: str) -> None:
        self.content = content
        self.messages = None

    def invoke(self, messages):
        self.messages = messages
        return FakeMessage(content=self.content)


def test_run_summary_tool_calls_llm() -> None:
    llm = FakeLLM("LangChain helps build LLM applications.")

    result = run_summary_tool(
        "  LangChain   helps build   LLM apps.  ",
        llm=llm,
    )

    assert result == {
        "summary": "LangChain helps build LLM applications.",
    }
    assert llm.messages is not None


def test_run_summary_tool_returns_fallback_for_empty_text() -> None:
    llm = FakeLLM("should not be used")

    result = run_summary_tool("   ", llm=llm)

    assert result == {
        "summary": "No text provided for summarization.",
    }
    assert llm.messages is None


def test_run_summary_tool_returns_fallback_for_empty_model_output() -> None:
    llm = FakeLLM("   ")

    result = run_summary_tool("LangChain helps build LLM apps.", llm=llm)

    assert result == {
        "summary": "The model returned an empty summary.",
    }


def test_run_summary_tool_caps_long_summary() -> None:
    llm = FakeLLM("abcdef")

    result = run_summary_tool("some input", llm=llm, max_chars=3)

    assert result == {
        "summary": "abc...",
    }
