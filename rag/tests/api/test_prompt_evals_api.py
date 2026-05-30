import json
from pathlib import Path
from typing import Any

from rag_app.config import config
from rag_app.services import prompt_eval_service


def write_report(
    path: Path,
    run_id: str,
    prompt_version: str,
    cases: list[dict[str, Any]] | None = None,
    passed: int = 1,
    failed: int = 0,
) -> None:
    report = {
        "run_id": run_id,
        "prompt_version": prompt_version,
        "total": passed + failed,
        "passed": passed,
        "failed": failed,
        "cases": cases or [],
    }

    path.write_text(
        json.dumps(report, ensure_ascii=False),
        encoding="utf-8",
    )


def test_list_prompt_eval_reports(client, tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(prompt_eval_service, "JUDGE_RUNS_DIR", tmp_path)

    write_report(
        tmp_path / "20260526-211450.json",
        run_id="20260526-211450",
        prompt_version="qa_prompt_v1",
        passed=11,
        failed=0,
    )

    response = client.get("/prompt-evals/reports")

    assert response.status_code == 200
    assert response.json() == [
        {
            "run_id": "20260526-211450",
            "prompt_version": "qa_prompt_v1",
            "total": 11,
            "passed": 11,
            "failed": 0,
            "created_at": "2026-05-26T21:14:50",
        }
    ]


def test_get_prompt_eval_report_by_run_id(
    client,
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(prompt_eval_service, "JUDGE_RUNS_DIR", tmp_path)

    write_report(
        tmp_path / "20260526-211450.json",
        run_id="20260526-211450",
        prompt_version="qa_prompt_v1",
        cases=[
            {
                "id": "case_1",
                "passed": True,
            }
        ],
    )

    response = client.get("/prompt-evals/reports/20260526-211450")

    assert response.status_code == 200
    assert response.json()["run_id"] == "20260526-211450"
    assert response.json()["cases"][0]["id"] == "case_1"


def test_get_prompt_eval_report_returns_404_when_missing(
    client,
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(prompt_eval_service, "JUDGE_RUNS_DIR", tmp_path)

    response = client.get("/prompt-evals/reports/missing")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "judge report not found: missing",
    }


def test_get_latest_prompt_comparison(client, tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(prompt_eval_service, "JUDGE_RUNS_DIR", tmp_path)
    monkeypatch.setattr(config, "QA_PROMPT_VERSION", "qa_prompt_v1")

    write_report(
        tmp_path / "20260526-200000.json",
        run_id="20260526-200000",
        prompt_version="qa_prompt_v1",
        cases=[
            {
                "judge": {
                    "relevance_score": 1,
                    "completeness_score": 1,
                    "groundedness_score": 1,
                    "format_score": 1,
                },
                "answer_duration_seconds": 1,
                "judge_duration_seconds": 1,
                "total_duration_seconds": 2,
            }
        ],
    )
    write_report(
        tmp_path / "20260526-211450.json",
        run_id="20260526-211450",
        prompt_version="qa_prompt_v1",
        cases=[
            {
                "judge": {
                    "relevance_score": 5,
                    "completeness_score": 4,
                    "groundedness_score": 5,
                    "format_score": 4,
                },
                "answer_duration_seconds": 10,
                "judge_duration_seconds": 20,
                "total_duration_seconds": 30,
            },
            {
                "judge": {
                    "relevance_score": 3,
                    "completeness_score": 4,
                    "groundedness_score": 5,
                    "format_score": 5,
                },
                "answer_duration_seconds": 20,
                "judge_duration_seconds": 30,
                "total_duration_seconds": 50,
            },
        ],
        passed=2,
        failed=0,
    )
    write_report(
        tmp_path / "20260526-212913.json",
        run_id="20260526-212913",
        prompt_version="qa_prompt_v2",
        cases=[
            {
                "judge": {
                    "relevance_score": 5,
                    "completeness_score": 5,
                    "groundedness_score": 4,
                    "format_score": 4,
                },
                "answer_duration_seconds": 40,
                "judge_duration_seconds": 60,
                "total_duration_seconds": 100,
            },
            {
                "judge": None,
                "answer_duration_seconds": 20,
                "judge_duration_seconds": 0,
                "total_duration_seconds": 20,
            },
        ],
        passed=1,
        failed=1,
    )

    response = client.get("/prompt-evals/comparison/latest")

    assert response.status_code == 200

    data = response.json()

    assert data["selected_prompt"] == "qa_prompt_v1"
    assert data["qa_prompt_v1"]["run_id"] == "20260526-211450"
    assert data["qa_prompt_v1"]["avg_relevance"] == 4.0
    assert data["qa_prompt_v1"]["avg_completeness"] == 4.0
    assert data["qa_prompt_v1"]["avg_groundedness"] == 5.0
    assert data["qa_prompt_v1"]["avg_format"] == 4.5
    assert data["qa_prompt_v1"]["avg_answer_duration"] == 15.0
    assert data["qa_prompt_v1"]["avg_judge_duration"] == 25.0
    assert data["qa_prompt_v1"]["avg_total_duration"] == 40.0

    assert data["qa_prompt_v2"]["run_id"] == "20260526-212913"
    assert data["qa_prompt_v2"]["avg_relevance"] == 5.0
    assert data["qa_prompt_v2"]["avg_answer_duration"] == 30.0
    assert data["qa_prompt_v2"]["avg_total_duration"] == 60.0


def test_get_latest_prompt_comparison_returns_404_when_missing_prompt_report(
    client,
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(prompt_eval_service, "JUDGE_RUNS_DIR", tmp_path)

    write_report(
        tmp_path / "20260526-211450.json",
        run_id="20260526-211450",
        prompt_version="qa_prompt_v1",
    )

    response = client.get("/prompt-evals/comparison/latest")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "missing qa_prompt_v1 or qa_prompt_v2 judge report",
    }
