from __future__ import annotations

from typing import Any

from rag_app.scripts.evaluate_retrieval import (
    RetrievalEvalCase,
    has_expected_sources,
    load_case,
)
from rag_app.services.ask_service import ask_question

FORBIDDEN_ANSWER_FRAGMENTS = (
    "data/raw/",
    "/Users/",
    "source:",
    "section_path",
    "page_content",
)


def get_answer_source_paths(result: dict[str, Any]) -> list[str]:
    sources = result.get("sources", [])

    if not isinstance(sources, list):
        return []

    return [
        str(source.get("source", ""))
        for source in sources
        if isinstance(source, dict)
    ]


def answer_has_forbidden_fragments(answer: str) -> bool:
    normalized_answer = answer.lower()
    return any(
        fragment.lower() in normalized_answer
        for fragment in FORBIDDEN_ANSWER_FRAGMENTS
    )


def evaluate_answer_result(
    case: RetrievalEvalCase,
    result: dict[str, Any],
) -> tuple[bool, list[str]]:
    failures: list[str] = []
    answer = str(result.get("answer", "")).strip()
    sources = get_answer_source_paths(result)

    if not answer:
        failures.append("answer is empty")

    if not sources:
        failures.append("sources are empty")

    if not has_expected_sources(
        sources=sources,
        expected_source_contains=case.expected_source_contains,
    ):
        failures.append("expected source not found")

    if answer_has_forbidden_fragments(answer):
        failures.append("answer contains source metadata")

    return len(failures) == 0, failures


def evaluate_case(case: RetrievalEvalCase) -> dict:
    result = ask_question(case.question)
    passed, failures = evaluate_answer_result(case, result)
    sources = get_answer_source_paths(result)
    status = "PASS" if passed else "FAIL"

    print(f"Evaluating answer {case.id} with {status}")
    print(f"question: {case.question}")

    if failures:
        print("failures:")
        for failure in failures:
            print(f"- {failure}")

    print("answer:")
    print(result.get("answer", ""))
    print("sources:")
    for source in sources:
        print(f"- {source}")

    print()

    return {
        "id": case.id,
        "question": case.question,
        "passed": passed,
        "failures": failures,
        "sources": sources,
    }


def run_evaluation() -> dict:
    cases = load_case()

    case_results = [
        evaluate_case(case)
        for case in cases
    ]

    passed_count = sum(result["passed"] for result in case_results)
    total_count = len(case_results)

    print(f"summary: {passed_count}/{total_count} passed")

    return {
        "passed": passed_count,
        "total": total_count,
        "cases": case_results,
    }


def main() -> None:
    summary = run_evaluation()

    if summary["passed"] != summary["total"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
