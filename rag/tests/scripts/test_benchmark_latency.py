import pytest

from rag_app.scripts import benchmark_latency
from rag_app.scripts.benchmark_latency import BenchmarkCase


def test_run_case_records_duration_and_result_metadata(monkeypatch) -> None:
    perf_counter_values = iter([10.0, 12.34])

    monkeypatch.setattr(
        benchmark_latency,
        "perf_counter",
        lambda: next(perf_counter_values),
    )
    monkeypatch.setattr(
        benchmark_latency,
        "ask_question",
        lambda question: {
            "answer": "RAG answer",
            "sources": [
                {
                    "source": "data/raw/rag-paper.pdf",
                },
                {
                    "source": "data/raw/qdrant-docs.md",
                },
            ],
            "trace": [
                {
                    "step": "retrieval",
                    "detail": {
                        "duration_seconds": 0.12,
                    },
                },
                {
                    "step": "generate_answer",
                    "detail": {
                        "duration_seconds": 2.22,
                    },
                },
            ],
        },
    )

    result = benchmark_latency.run_case(
        BenchmarkCase(
            case_id="rag_definition",
            question="What is RAG?",
        )
    )

    assert result == {
        "case_id": "rag_definition",
        "question": "What is RAG?",
        "total_duration_seconds": 2.34,
        "retrieval_duration_seconds": 0.12,
        "generation_duration_seconds": 2.22,
        "answer_length": len("RAG answer"),
        "source_count": 2,
    }


def test_get_trace_duration_returns_zero_when_step_has_no_duration() -> None:
    result = {
        "trace": [
            {
                "step": "generate_answer",
                "detail": {
                    "attempt": 1,
                },
            }
        ]
    }

    assert benchmark_latency.get_trace_duration(result, "generate_answer") == 0.0


def test_run_benchmark_summarizes_case_durations(monkeypatch) -> None:
    fake_results = [
        {
            "case_id": "case_1",
            "question": "Question 1",
            "total_duration_seconds": 1.0,
            "retrieval_duration_seconds": 0.1,
            "generation_duration_seconds": 0.9,
            "answer_length": 10,
            "source_count": 1,
        },
        {
            "case_id": "case_2",
            "question": "Question 2",
            "total_duration_seconds": 3.0,
            "retrieval_duration_seconds": 0.2,
            "generation_duration_seconds": 2.8,
            "answer_length": 20,
            "source_count": 2,
        },
    ]
    fake_cases = (
        BenchmarkCase(case_id="case_1", question="Question 1"),
        BenchmarkCase(case_id="case_2", question="Question 2"),
    )

    monkeypatch.setattr(benchmark_latency, "BENCHMARK_CASES", fake_cases)
    monkeypatch.setattr(
        benchmark_latency,
        "run_case",
        lambda case: fake_results[0] if case.case_id == "case_1" else fake_results[1],
    )

    report = benchmark_latency.run_benchmark()

    assert report == {
        "total_cases": 2,
        "top_k": benchmark_latency.config.RETRIEVAL_TOP_K,
        "average_duration_seconds": 2.0,
        "max_duration_seconds": 3.0,
        "min_duration_seconds": 1.0,
        "cases": fake_results,
    }


def test_run_benchmark_does_not_accept_runtime_top_k_override() -> None:
    with pytest.raises(TypeError):
        benchmark_latency.run_benchmark(top_k=3)
