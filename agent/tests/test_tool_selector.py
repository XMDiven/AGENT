from typing import Any

import pytest
from langchain_core.messages import HumanMessage, SystemMessage

from agent_app.orchestration.tool_selector import (
    build_openai_tools,
    select_tool_with_llm,
)


class FakeMessage:
    def __init__(self, tool_calls: list[dict[str, Any]]) -> None:
        self.tool_calls = tool_calls


class FakeBoundLLM:
    def __init__(self, message: FakeMessage) -> None:
        self.message = message
        self.messages: list[Any] = []

    def invoke(self, messages: list[Any]) -> FakeMessage:
        self.messages = messages
        return self.message


class FakeLLM:
    def __init__(self, message: FakeMessage) -> None:
        self.bound_llm = FakeBoundLLM(message)
        self.tools: list[dict[str, Any]] = []
        self.tool_choice: str | None = None

    def bind_tools(
        self,
        tools: list[dict[str, Any]],
        tool_choice: str,
    ) -> FakeBoundLLM:
        self.tools = tools
        self.tool_choice = tool_choice
        return self.bound_llm


def test_build_openai_tools_uses_registered_tool_schemas() -> None:
    tools = build_openai_tools()

    retrieval_tool = tools[0]

    assert retrieval_tool["type"] == "function"
    assert retrieval_tool["function"]["name"] == "retrieval_tool"
    assert retrieval_tool["function"]["parameters"]["required"] == ["question"]


def test_select_tool_with_llm_returns_first_tool_call() -> None:
    llm = FakeLLM(
        FakeMessage(
            [
                {
                    "name": "retrieval_tool",
                    "args": {"question": "What is RAG?"},
                }
            ]
        )
    )

    selection = select_tool_with_llm(question="What is RAG?", llm=llm)

    assert llm.tool_choice == "auto"
    assert llm.tools[0]["function"]["name"] == "retrieval_tool"
    assert isinstance(llm.bound_llm.messages[0], SystemMessage)
    assert isinstance(llm.bound_llm.messages[1], HumanMessage)
    assert selection.tool.name == "retrieval_tool"
    assert selection.tool_args == {"question": "What is RAG?"}
    assert selection.reason == "llm selected tool via native tool calling"


def test_select_tool_with_llm_raises_when_model_returns_no_tool_call() -> None:
    llm = FakeLLM(FakeMessage([]))

    with pytest.raises(ValueError, match="LLM did not return a tool call"):
        select_tool_with_llm(question="What is RAG?", llm=llm)


def test_select_tool_with_llm_raises_for_unknown_tool() -> None:
    llm = FakeLLM(
        FakeMessage(
            [
                {
                    "name": "unknown_tool",
                    "args": {},
                }
            ]
        )
    )

    with pytest.raises(ValueError, match="Unknown tool: unknown_tool"):
        select_tool_with_llm(question="What is RAG?", llm=llm)
