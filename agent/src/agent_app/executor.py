from dataclasses import dataclass
from typing import Any

from agent_app.planner import AgentPlan
from agent_app.retrieval_tool import run_retrieval_tool
from agent_app.summary_tool import run_summary_tool


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
        try:
            result = run_retrieval_tool(question)
        except Exception as error:
            return ToolResult(
                tool_name=plan.tool.name,
                status="failed",
                output={
                    "error_type": type(error).__name__,
                    "error": str(error),
                },
            )
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

    if plan.tool.name == "summary_tool":
        text = str((tool_input or {}).get("text", ""))

        return ToolResult(
            tool_name=plan.tool.name,
            status="success",
            output=run_summary_tool(text),
        )

    return ToolResult(
        tool_name=plan.tool.name,
        status="failed",
        output={
            "error": f"Unsupported tool: {plan.tool.name}",
        },
    )
