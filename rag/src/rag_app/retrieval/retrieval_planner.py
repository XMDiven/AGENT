from dataclasses import dataclass

from rag_app.config import config
from rag_app.retrieval.query_analyzer import QueryAnalysis


@dataclass(frozen=True)
class RetrievalPlan:
    retrieval_strategy: str
    retrieval_query: str
    top_k: int
    reason: str


def plan_retrieval(analysis: QueryAnalysis) -> RetrievalPlan:
    if analysis.question_type == "empty" or not analysis.needs_retrieval:
        return RetrievalPlan(
            retrieval_strategy="skip_retrieval",
            retrieval_query="",
            top_k=0,
            reason="empty questions do not need retrieval",
        )

    if analysis.question_type == "comparison":
        return RetrievalPlan(
            retrieval_strategy="comparison_retrieval",
            retrieval_query=analysis.normalized_question,
            top_k=config.RETRIEVAL_TOP_K,
            reason="comparison questions may need evidence from multiple sources",
        )

    return RetrievalPlan(
        retrieval_strategy="standard_retrieval",
        retrieval_query=analysis.normalized_question,
        top_k=config.RETRIEVAL_TOP_K,
        reason="general knowledge questions use standard retrieval",
    )
