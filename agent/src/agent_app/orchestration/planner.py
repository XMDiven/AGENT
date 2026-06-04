import logging
from dataclasses import dataclass
from typing import Any

from agent_app.orchestration.tool_selector import select_tool_with_llm
from agent_app.tools.question_decompose import has_decomposition_signal
from agent_app.tools.registry import ToolDefinition, get_tool

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AgentPlan:
    tool: ToolDefinition
    reason: str
    tool_args: dict[str, Any] | None = None


def plan_tool_by_rules(question_type: str, question: str = "") -> AgentPlan:
    if question_type == "empty":
        return AgentPlan(
            tool=get_tool("fallback_tool"),
            reason="question does not require retrieval",
        )

    if has_decomposition_signal(question):
        return AgentPlan(
            tool=get_tool("question_decompose_tool"),
            reason="question contains comparison or multi-part intent",
        )

    if question_type == "summary":
        return AgentPlan(
            tool=get_tool("summary_tool"),
            reason="question asks for summarization",
        )

    return AgentPlan(
        tool=get_tool("retrieval_tool"),
        reason="question requires knowledge retrieval",
    )


def plan_tool(question_type: str, question: str = "") -> AgentPlan:
    if question_type == "empty":
        return plan_tool_by_rules(question_type=question_type, question=question)

    try:
        selection = select_tool_with_llm(question=question)
    except Exception as exc:
        logger.warning(
            "agent.tool_selection fallback question_type=%s error_type=%s",
            question_type,
            type(exc).__name__,
        )
        return plan_tool_by_rules(question_type=question_type, question=question)

    return AgentPlan(
        tool=selection.tool,
        reason=selection.reason,
        tool_args=selection.tool_args,
    )
