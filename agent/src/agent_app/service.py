from dataclasses import dataclass
from typing import Any

from rag_app.retrieval.query_analyzer import analyze_query

from agent_app.orchestration.executor import ToolResult, execute_plan
from agent_app.orchestration.planner import AgentPlan, plan_tool
from agent_app.orchestration.state import AgentState


@dataclass(frozen=True)
class AgentRunResult:
    plan: AgentPlan
    tool_result: ToolResult
    trace: list[dict[str, Any]]


def run_agent(question: str) -> AgentRunResult:
    analysis = analyze_query(question)

    plan = plan_tool(
        question_type=analysis.question_type,
        question=question,
    )

    tool_input = (
        plan.tool_args
        if plan.tool_args is not None
        else {
            "question": question,
            "text": question,
        }
    )

    tool_result = execute_plan(
        plan=plan,
        tool_input=tool_input,
    )

    execute_detail: dict[str, Any] = {
        "tool_name": tool_result.tool_name,
        "attempts": tool_result.attempts,
    }

    if (
        tool_result.tool_name == "question_decompose_tool"
        and isinstance(tool_result.output, dict)
    ):
        sub_questions = tool_result.output.get("sub_questions", [])
        execute_detail["decomposition_strategy"] = tool_result.output.get(
            "decomposition_strategy"
        )

        execute_detail["sub_question_count"] = (
            len(sub_questions) if isinstance(sub_questions, list) else 0
        )

    trace = [
        {
            "step": "analyze_question",
            "status": "completed",
            "detail": {
                "needs_retrieval": analysis.needs_retrieval,
                "question_type": analysis.question_type,
                "reason": analysis.reason,
            },
        },
        {
            "step": "plan_tool",
            "status": "completed",
            "detail": {
                "tool_name": plan.tool.name,
                "reason": plan.reason,
            },
        },
        {
            "step": "execute_tool",
            "status": tool_result.status,
            "detail": execute_detail,
        },
    ]

    state = AgentState(
        question=question,
        analysis=analysis,
        plan=plan,
        tool_result=tool_result,
        trace=trace,
    )

    return AgentRunResult(
        plan=state.plan,
        tool_result=state.tool_result,
        trace=state.trace,
    )
