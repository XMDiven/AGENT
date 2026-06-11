from dataclasses import dataclass
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from agent_app.prompts import PLANNER_SYSTEM_PROMPT
from agent_app.tools import get_tool, list_tools, ToolDefinition
from rag_app.infrastructure.llm_client import get_client


@dataclass(frozen=True)
class ToolSelection:
    tool: ToolDefinition
    tool_args: dict[str, Any]
    reason: str


def build_openai_tools() -> list[dict[str, Any]]:
    return [
        {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.input_schema,
            },
        }
        for tool in list_tools()
    ]


def select_tool_with_llm(
    question: str,
    llm: ChatOpenAI | None = None,
) -> ToolSelection:
    client = llm or get_client()
    tool_calling_llm = client.bind_tools(
        build_openai_tools(),
        tool_choice="auto",
    )

    message = tool_calling_llm.invoke(
        [
            SystemMessage(content=PLANNER_SYSTEM_PROMPT),
            HumanMessage(content=question),
        ]
    )

    tool_calls = getattr(message, "tool_calls", None) or []
    if not tool_calls:
        raise ValueError("LLM did not return a tool call")

    tool_call = tool_calls[0]
    tool = get_tool(tool_call["name"])
    tool_args = tool_call.get("args") or {}

    return ToolSelection(
        tool=tool,
        tool_args=tool_args,
        reason="llm selected tool via native tool calling",
    )
