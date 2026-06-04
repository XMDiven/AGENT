from agent_app.orchestration.planner import plan_tool, plan_tool_by_rules
from agent_app.orchestration.tool_selector import ToolSelection
from agent_app.tools import get_tool


def test_plan_tool_by_rules_selects_fallback_tool_for_empty_question() -> None:
    plan = plan_tool_by_rules(question_type="empty")

    assert plan.tool.name == "fallback_tool"
    assert plan.reason == "question does not require retrieval"


def test_plan_tool_by_rules_selects_summary_tool_for_summary_question() -> None:
    plan = plan_tool_by_rules(question_type="summary")

    assert plan.tool.name == "summary_tool"
    assert plan.reason == "question asks for summarization"


def test_plan_tool_by_rules_selects_question_decompose_tool_for_comparison_question() -> None:
    plan = plan_tool_by_rules(
        question_type="general",
        question="LangChain 和 LlamaIndex 分别适合做什么？",
    )

    assert plan.tool.name == "question_decompose_tool"
    assert plan.reason == "question contains comparison or multi-part intent"


def test_plan_tool_by_rules_selects_retrieval_tool_for_general_question() -> None:
    plan = plan_tool_by_rules(question_type="general")

    assert plan.tool.name == "retrieval_tool"
    assert plan.reason == "question requires knowledge retrieval"


def test_plan_tool_uses_llm_tool_selection(monkeypatch) -> None:
    def fake_select_tool_with_llm(question: str) -> ToolSelection:
        assert question == "What is RAG?"
        return ToolSelection(
            tool=get_tool("retrieval_tool"),
            tool_args={"question": "What is RAG?"},
            reason="llm selected tool via native tool calling",
        )

    monkeypatch.setattr(
        "agent_app.orchestration.planner.select_tool_with_llm",
        fake_select_tool_with_llm,
    )

    plan = plan_tool(question_type="general", question="What is RAG?")

    assert plan.tool.name == "retrieval_tool"
    assert plan.reason == "llm selected tool via native tool calling"
    assert plan.tool_args == {"question": "What is RAG?"}


def test_plan_tool_falls_back_to_rules_when_llm_selection_fails(
    monkeypatch,
) -> None:
    def raise_error(question: str) -> None:
        raise RuntimeError("tool calling unavailable")

    monkeypatch.setattr(
        "agent_app.orchestration.planner.select_tool_with_llm",
        raise_error,
    )

    plan = plan_tool(question_type="summary", question="请总结 LangChain")

    assert plan.tool.name == "summary_tool"
    assert plan.reason == "question asks for summarization"
    assert plan.tool_args is None


def test_plan_tool_does_not_call_llm_for_empty_question(monkeypatch) -> None:
    def raise_error(question: str) -> None:
        raise AssertionError("empty questions should not call the LLM planner")

    monkeypatch.setattr(
        "agent_app.orchestration.planner.select_tool_with_llm",
        raise_error,
    )

    plan = plan_tool(question_type="empty")

    assert plan.tool.name == "fallback_tool"
    assert plan.reason == "question does not require retrieval"
