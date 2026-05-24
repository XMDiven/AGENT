from __future__ import annotations

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


def summarize_trace_step(result: dict[str, Any], step: str) -> dict[str, Any]:
    duration_seconds = 0.0
    status = "missing"
    error_type = ""

    for item in result.get("trace", []):
        if item.get("step") != step:
            continue

        status = str(item.get("status", "unknown"))

        detail = item.get("detail", {})
        duration_seconds += float(detail.get("duration_seconds", 0.0))

        if detail.get("error_type"):
            error_type = str(detail["error_type"])

    return {
        "duration_seconds": round(duration_seconds, 2),
        "status": status,
        "error_type": error_type,
    }


def run_case(case: BenchmarkCase) -> dict[str, Any]:
    start = perf_counter()
    result = ask_question(case.question)
    duration_seconds = perf_counter() - start

    retrieval_summary = summarize_trace_step(result, "retrieval")
    generation_summary = summarize_trace_step(result, "generate_answer")
    answer = str(result.get("answer", ""))

    generation_status = generation_summary["status"]

    return {
        "case_id": case.case_id,
        "question": case.question,
        "total_duration_seconds": round(duration_seconds, 2),
        "retrieval_duration_seconds": retrieval_summary["duration_seconds"],
        "generation_duration_seconds": generation_summary["duration_seconds"],
        "generation_status": generation_status,
        "generation_error_type": (
            generation_summary["error_type"]
            if generation_status == "failed"
            else ""
        ),
        "answer_is_fallback": answer == config.FALLBACK_ANSWER,
        "answer_preview": answer[:120],
        "answer_length": len(answer),
        "source_count": len(result.get("sources", [])),
    }


def run_benchmark() -> dict[str, Any]:
    results: list[dict[str, Any]] = [run_case(case) for case in BENCHMARK_CASES]
    durations = [result["total_duration_seconds"] for result in results]

    return {
        "total_cases": len(results),
        "top_k": config.RETRIEVAL_TOP_K,
        "average_duration_seconds": round(mean(durations), 2),
        "max_duration_seconds": round(max(durations), 2),
        "min_duration_seconds": round(min(durations), 2),
        "cases": results,
    }


def main() -> None:
    report = run_benchmark()

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
        print(f"generation_status: {case['generation_status']}")
        print(f"generation_error_type: {case['generation_error_type']}")
        print(f"answer_is_fallback: {case['answer_is_fallback']}")
        print(f"answer_preview: {case['answer_preview']}")
        print()


if __name__ == "__main__":
    main()
