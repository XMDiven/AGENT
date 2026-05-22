from dataclasses import dataclass
from typing import Any

from agent_app.planner import AgentPlan
from agent_app.retrieval_tool import run_retrieval_tool
from agent_app.summary_tool import run_summary_tool

MAX_TOOL_ATTEMPTS = 3


@dataclass(frozen=True)
class ToolResult:
    tool_name: str
    status: str
    output: Any
    attempts: list[dict[str, Any]]


def execute_plan(
    plan: AgentPlan,
    tool_input: dict[str, Any] | None = None,
    max_attempts: int = MAX_TOOL_ATTEMPTS,
) -> ToolResult:
    if plan.tool.name == "retrieval_tool":
        question = str((tool_input or {}).get("question", ""))
        attempts: list[dict[str, Any]] = []
        last_error: Exception | None = None

        for attempt in range(1, max(1, max_attempts) + 1):
            try:
                result = run_retrieval_tool(question)
            except Exception as error:
                last_error = error
                attempts.append(
                    {
                        "attempt": attempt,
                        "status": "failed",
                        "error_type": type(error).__name__,
                        "error": str(error),
                    }
                )
                continue

            attempts.append(
                {
                    "attempt": attempt,
                    "status": "success",
                }
            )

            return ToolResult(
                tool_name=plan.tool.name,
                status="success",
                output=result,
                attempts=attempts,
            )

        return ToolResult(
            tool_name=plan.tool.name,
            status="failed",
            output={
                "error_type": type(last_error).__name__,
                "error": str(last_error),
            },
            attempts=attempts,
        )

    if plan.tool.name == "fallback_tool":
        return ToolResult(
            tool_name=plan.tool.name,
            status="success",
            output={
                "answer": "No retrieval is needed for this question.",
                "sources": [],
            },
            attempts=[
                {
                    "attempt": 1,
                    "status": "success",
                }
            ],
        )

    if plan.tool.name == "summary_tool":
        text = str((tool_input or {}).get("text", ""))

        return ToolResult(
            tool_name=plan.tool.name,
            status="success",
            output=run_summary_tool(text),
            attempts=[
                {
                    "attempt": 1,
                    "status": "success",
                }
            ],
        )

    return ToolResult(
        tool_name=plan.tool.name,
        status="failed",
        output={
            "error": f"Unsupported tool: {plan.tool.name}",
        },
        attempts=[
            {
                "attempt": 1,
                "status": "failed",
                "error": f"Unsupported tool: {plan.tool.name}",
            }
        ],
    )
