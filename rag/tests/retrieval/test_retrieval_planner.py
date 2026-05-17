from rag_app.config import config
from rag_app.retrieval.query_analyzer import analyze_query
from rag_app.retrieval.retrieval_planner import plan_retrieval


def test_plan_retrieval_skips_empty_question() -> None:
    analysis = analyze_query("   ")

    plan = plan_retrieval(analysis)

    assert plan.retrieval_strategy == "skip_retrieval"
    assert plan.retrieval_query == ""
    assert plan.top_k == 0
    assert plan.reason == "empty questions do not need retrieval"


def test_plan_retrieval_uses_standard_strategy_for_general_question() -> None:
    analysis = analyze_query("Qdrant 是什么？")

    plan = plan_retrieval(analysis)

    assert plan.retrieval_strategy == "standard_retrieval"
    assert plan.retrieval_query == "Qdrant 是什么？"
    assert plan.top_k == config.RETRIEVAL_TOP_K
    assert plan.reason == "general knowledge questions use standard retrieval"


def test_plan_retrieval_uses_comparison_strategy_for_comparison_question() -> None:
    question = "LangChain 和 LlamaIndex 分别适合做什么？"
    analysis = analyze_query(question)

    plan = plan_retrieval(analysis)

    assert plan.retrieval_strategy == "comparison_retrieval"
    assert plan.retrieval_query == question
    assert plan.top_k == config.RETRIEVAL_TOP_K
    assert plan.reason == "comparison questions may need evidence from multiple sources"
