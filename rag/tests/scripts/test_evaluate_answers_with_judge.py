from dataclasses import dataclass

from rag_app.evaluation.judge_schema import AnswerJudgeResult
from rag_app.scripts import evaluate_answers_with_judge


@dataclass(frozen=True)
class DummyCase:
    id: str
    question: str


def test_evaluate_case_records_judge_result(monkeypatch) -> None:
    case = DummyCase(id="qdrant_usage", question="What is Qdrant used for?")

    monkeypatch.setattr(
        evaluate_answers_with_judge,
        "ask_question",
        lambda question: {
            "answer": "Qdrant is used for vector search.",
            "sources": [
                {
                    "source": "data/raw/qdrant-docs.md",
                    "section_path": "overview",
                    "snippet": "Qdrant is a vector database.",
                }
            ],
        },
    )
    monkeypatch.setattr(
        evaluate_answers_with_judge,
        "judge_answer",
        lambda question, answer, sources, llm: AnswerJudgeResult(
            relevance_score=5,
            completeness_score=4,
            groundedness_score=5,
            format_score=4,
            overall_pass=True,
            feedback="good answer",
        ),
    )

    result = evaluate_answers_with_judge.evaluate_case(case, llm=object())

    assert result["passed"] is True
    assert result["failures"] == []
    assert result["judge"]["groundedness_score"] == 5
    assert result["answer_duration_seconds"] >= 0
    assert result["judge_duration_seconds"] >= 0
    assert result["total_duration_seconds"] >= 0


def test_evaluate_case_records_failure_when_judge_raises(monkeypatch) -> None:
    case = DummyCase(id="qdrant_usage", question="What is Qdrant used for?")

    monkeypatch.setattr(
        evaluate_answers_with_judge,
        "ask_question",
        lambda question: {
            "answer": "Qdrant is used for vector search.",
            "sources": [],
        },
    )

    def raise_judge_error(question, answer, sources, llm):
        raise ValueError("invalid judge json")

    monkeypatch.setattr(
        evaluate_answers_with_judge,
        "judge_answer",
        raise_judge_error,
    )

    result = evaluate_answers_with_judge.evaluate_case(case, llm=object())

    assert result["passed"] is False
    assert result["judge"] is None
    assert result["failures"] == ["judge failed"]
    assert result["judge_error"] == {
        "error_type": "ValueError",
        "error": "invalid judge json",
    }
    assert result["answer_duration_seconds"] >= 0
    assert result["judge_duration_seconds"] >= 0
    assert result["total_duration_seconds"] >= 0


def test_run_evaluation_prints_case_progress(monkeypatch, capsys) -> None:
    cases = [
        DummyCase(id="case_one", question="Question one?"),
        DummyCase(id="case_two", question="Question two?"),
    ]

    monkeypatch.setattr(
        evaluate_answers_with_judge,
        "load_case",
        lambda: cases,
    )
    monkeypatch.setattr(
        evaluate_answers_with_judge,
        "get_client",
        lambda: object(),
    )
    monkeypatch.setattr(
        evaluate_answers_with_judge,
        "evaluate_case",
        lambda case, llm: {
            "id": case.id,
            "question": case.question,
            "answer": "answer",
            "sources": [],
            "judge": {},
            "passed": True,
            "failures": [],
            "answer_duration_seconds": 1.0,
            "judge_duration_seconds": 2.0,
            "total_duration_seconds": 3.0,
        },
    )

    summary = evaluate_answers_with_judge.run_evaluation()
    output = capsys.readouterr().out

    assert summary["passed"] == 2
    assert "Evaluating judge case 1/2: case_one" in output
    assert "completed case_one passed=True total=3.0s" in output
    assert "Evaluating judge case 2/2: case_two" in output
