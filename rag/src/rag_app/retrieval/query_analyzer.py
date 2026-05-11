from dataclasses import dataclass


@dataclass
class QueryAnalysis:
    original_question: str
    normalized_question: str
    needs_retrieval: bool
    reason: str


def analyze_query(question: str) -> QueryAnalysis:
    normalized_question = " ".join(question.split()).strip()
    if not normalized_question:
        return QueryAnalysis(
            original_question=question,
            normalized_question="",
            needs_retrieval=False,
            reason="empty question",
        )

    return QueryAnalysis(
        original_question=question,
        normalized_question=normalized_question,
        needs_retrieval=True,
        reason="normal knowledge question, use retrieval",
    )
