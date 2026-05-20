from dataclasses import dataclass
from typing import Any

from agent_app.planner import AgentPlan


@dataclass(frozen=True)
class ToolResult:
    tool_name: str
    status: str
    output: Any


def execute_plan(plan: AgentPlan) -> ToolResult:
    if plan.tool.name == "retrieval_tool":
        return ToolResult(
            tool_name=plan.tool.name,
            status="not_implemented",
            output={
                "reason": "retrieval_tool is registered but not wired to RAG yet",
            },
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
