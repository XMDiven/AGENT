from agent_app.planner import plan_tool


def test_plan_tool_selects_retrieval_tool_when_retrieval_is_needed() -> None:
    plan = plan_tool(needs_retrieval=True)

    assert plan.tool.name == "retrieval_tool"
    assert plan.reason == "question requires knowledge retrieval"


def test_plan_tool_selects_fallback_tool_when_retrieval_is_not_needed() -> None:
    plan = plan_tool(needs_retrieval=False)

    assert plan.tool.name == "fallback_tool"
    assert plan.reason == "question does not require retrieval"
