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
        "duration_seconds": 2.34,
        "answer_length": len("RAG answer"),
        "source_count": 2,
    }


def test_run_benchmark_summarizes_case_durations(monkeypatch) -> None:
    fake_results = [
        {
            "case_id": "case_1",
            "question": "Question 1",
            "duration_seconds": 1.0,
            "answer_length": 10,
            "source_count": 1,
        },
        {
            "case_id": "case_2",
            "question": "Question 2",
            "duration_seconds": 3.0,
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
        "average_duration_seconds": 2.0,
        "max_duration_seconds": 3.0,
        "min_duration_seconds": 1.0,
        "cases": fake_results,
    }
