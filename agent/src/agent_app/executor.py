from dataclasses import dataclass
from typing import Any

from agent_app.planner import AgentPlan
from agent_app.retrieval_tool import run_retrieval_tool


@dataclass(frozen=True)
class ToolResult:
    tool_name: str
    status: str
    output: Any


def execute_plan(
    plan: AgentPlan,
    tool_input: dict[str, Any] | None = None,
) -> ToolResult:
    if plan.tool.name == "retrieval_tool":
        question = str((tool_input or {}).get("question", ""))
        result = run_retrieval_tool(question)

        return ToolResult(
            tool_name=plan.tool.name,
            status="success",
            output=result,
        )

    if plan.tool.name == "fallback_tool":
        return ToolResult(
            tool_name=plan.tool.name,
            status="success",
            output={
                "answer": "No retrieval is needed for this question.",
                "sources": [],
            },
        )

    return ToolResult(
        tool_name=plan.tool.name,
        status="failed",
        output={
            "error": f"Unsupported tool: {plan.tool.name}",
        },
    )
