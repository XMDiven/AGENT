from agent_app.planner import plan_tool


def test_plan_tool_selects_fallback_tool_for_empty_question() -> None:
    plan = plan_tool(question_type="empty")

    assert plan.tool.name == "fallback_tool"
    assert plan.reason == "question does not require retrieval"


def test_plan_tool_selects_summary_tool_for_summary_question() -> None:
    plan = plan_tool(question_type="summary")

    assert plan.tool.name == "summary_tool"
    assert plan.reason == "question asks for summarization"


def test_plan_tool_selects_retrieval_tool_for_general_question() -> None:
    plan = plan_tool(question_type="general")

    assert plan.tool.name == "retrieval_tool"
    assert plan.reason == "question requires knowledge retrieval"
