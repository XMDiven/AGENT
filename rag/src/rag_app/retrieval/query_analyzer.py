from dataclasses import dataclass


@dataclass
class QueryAnalysis:
    original_question: str
    normalized_question: str
    needs_retrieval: bool
    reason: str
    question_type: str


def classify_question_type(question: str) -> str:
    normalized_question = question.lower()
    comparison_markers = (
        "比较",
        "区别",
        "分别",
        "各自",
        " vs ",
        " versus ",
        "compare ",
    )

    if any(marker in normalized_question for marker in comparison_markers):
        return "comparison"

    return "general"


def analyze_query(question: str) -> QueryAnalysis:
    normalized_question = " ".join(question.split()).strip()
    if not normalized_question:
        return QueryAnalysis(
            original_question=question,
            normalized_question="",
            needs_retrieval=False,
            reason="empty question",
            question_type="empty",
        )

    question_type = classify_question_type(normalized_question)
    reason = (
        "comparison question, use retrieval"
        if question_type == "comparison"
        else "normal knowledge question, use retrieval"
    )

    return QueryAnalysis(
        original_question=question,
        normalized_question=normalized_question,
        needs_retrieval=True,
        reason=reason,
        question_type=question_type,
    )
