from __future__ import annotations

from typing import Any

from src.scripts.evaluate_retrieval import (
    RetrievalEvalCase,
    has_expected_sources,
    load_case,
)
from src.services.ask_service import ask_question

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


def evaluate_case(case: RetrievalEvalCase) -> bool:
    result = ask_question(case.question)
    passed, failures = evaluate_answer_result(case, result)
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
    for source in get_answer_source_paths(result):
        print(f"- {source}")

    print()

    return passed


def main() -> None:
    cases = load_case()
    results = [
        evaluate_case(case)
        for case in cases
    ]

    passed_count = sum(results)
    total_count = len(results)

    print(f"summary: {passed_count}/{total_count} passed")

    if passed_count != total_count:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
