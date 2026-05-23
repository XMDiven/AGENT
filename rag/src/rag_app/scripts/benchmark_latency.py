from __future__ import annotations

import argparse
from dataclasses import dataclass
from statistics import mean
from time import perf_counter
from typing import Any

from rag_app.config import config
from rag_app.services.ask_service import ask_question


@dataclass(frozen=True)
class BenchmarkCase:
    case_id: str
    question: str


BENCHMARK_CASES: tuple[BenchmarkCase, ...] = (
    BenchmarkCase(
        case_id="rag_definition",
        question="What does retrieval augmented generation combine?",
    ),
    BenchmarkCase(
        case_id="qdrant_usage",
        question="What is Qdrant used for in vector search?",
    ),
    BenchmarkCase(
        case_id="langchain_usage",
        question="What is LangChain used for?",
    ),
)


def get_trace_duration(result: dict[str, Any], step: str) -> float:
    for item in result.get("trace", []):
        if item.get("step") == step:
            detail = item.get("detail", {})
            return float(detail.get("duration_seconds", 0.0))

    return 0.0


def run_case(case: BenchmarkCase) -> dict[str, Any]:
    start = perf_counter()
    result = ask_question(case.question)
    duration_seconds = perf_counter() - start

    return {
        "case_id": case.case_id,
        "question": case.question,
        "total_duration_seconds": round(duration_seconds, 2),
        "retrieval_duration_seconds": get_trace_duration(result, "retrieval"),
        "generation_duration_seconds": get_trace_duration(result, "generate_answer"),
        "answer_length": len(result.get("answer", "")),
        "source_count": len(result.get("sources", [])),
    }


def run_benchmark(top_k: int | None = None) -> dict[str, Any]:
    original_top_k = config.RETRIEVAL_TOP_K
    effective_top_k = top_k if top_k is not None else original_top_k

    try:
        if top_k is not None:
            config.RETRIEVAL_TOP_K = top_k

        results: list[dict[str, Any]] = [
            run_case(case) for case in BENCHMARK_CASES
        ]
        durations = [result["total_duration_seconds"] for result in results]
    finally:
        config.RETRIEVAL_TOP_K = original_top_k

    return {
        "total_cases": len(results),
        "top_k": effective_top_k,
        "average_duration_seconds": round(mean(durations), 2),
        "max_duration_seconds": round(max(durations), 2),
        "min_duration_seconds": round(min(durations), 2),
        "cases": results,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the RAG latency benchmark.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=None,
        help="Temporarily override RETRIEVAL_TOP_K for this benchmark run.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = run_benchmark(top_k=args.top_k)

    print("Latency benchmark summary")
    print(f"total cases: {report['total_cases']}")
    print(f"top_k: {report['top_k']}")
    print(f"average duration: {report['average_duration_seconds']}s")
    print(f"max duration: {report['max_duration_seconds']}s")
    print(f"min duration: {report['min_duration_seconds']}s")
    print()

    for case in report["cases"]:
        print(f"{case['case_id']}: {case['total_duration_seconds']}s")
        print(f"retrieval: {case['retrieval_duration_seconds']}s")
        print(f"generation: {case['generation_duration_seconds']}s")
        print()


if __name__ == "__main__":
    main()
