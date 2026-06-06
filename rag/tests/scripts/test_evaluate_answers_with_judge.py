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


def test_evaluate_case_passes_retrieval_options_to_ask_question(
    monkeypatch,
) -> None:
    case = DummyCase(id="qdrant_usage", question="What is Qdrant used for?")
    calls = []

    def fake_ask_question(question, **kwargs):
        calls.append(
            {
                "question": question,
                **kwargs,
            }
        )
        return {
            "answer": "Qdrant is used for vector search.",
            "sources": [],
        }

    monkeypatch.setattr(
        evaluate_answers_with_judge,
        "ask_question",
        fake_ask_question,
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

    evaluate_answers_with_judge.evaluate_case(
        case,
        llm=object(),
        top_k=7,
        search_type="mmr",
        fetch_k=50,
        lambda_mult=0.3,
    )

    assert calls == [
        {
            "question": "What is Qdrant used for?",
            "top_k": 7,
            "search_type": "mmr",
            "fetch_k": 50,
            "lambda_mult": 0.3,
        }
    ]


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


def test_run_evaluation_uses_custom_cases(monkeypatch) -> None:
    def fail_load_case():
        raise AssertionError("default cases should not be loaded")

    monkeypatch.setattr(
        evaluate_answers_with_judge,
        "load_case",
        fail_load_case,
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

    summary = evaluate_answers_with_judge.run_evaluation(
        cases=[
            {
                "id": "custom_case",
                "question": "Custom question?",
            }
        ]
    )

    assert summary["case_source"] == "custom"
    assert summary["total"] == 1
    assert summary["passed"] == 1
    assert summary["cases"][0]["id"] == "custom_case"
    assert summary["cases"][0]["question"] == "Custom question?"


def test_run_evaluation_records_retrieval_config(monkeypatch) -> None:
    cases = [
        DummyCase(id="case_one", question="Question one?"),
    ]
    calls = []

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

    def fake_evaluate_case(case, llm, **kwargs):
        calls.append(kwargs)
        return {
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
        }

    monkeypatch.setattr(
        evaluate_answers_with_judge,
        "evaluate_case",
        fake_evaluate_case,
    )

    summary = evaluate_answers_with_judge.run_evaluation(
        top_k=7,
        search_type="mmr",
        fetch_k=50,
        lambda_mult=0.3,
    )

    assert calls == [
        {
            "top_k": 7,
            "search_type": "mmr",
            "fetch_k": 50,
            "lambda_mult": 0.3,
        }
    ]
    assert summary["retrieval_config"] == {
        "top_k": 7,
        "search_type": "mmr",
        "fetch_k": 50,
        "lambda_mult": 0.3,
    }


def test_run_evaluation_applies_case_limit_to_custom_cases(monkeypatch) -> None:
    evaluated_case_ids: list[str] = []

    monkeypatch.setattr(
        evaluate_answers_with_judge,
        "get_client",
        lambda: object(),
    )

    def fake_evaluate_case(case, llm):
        evaluated_case_ids.append(case.id)

        return {
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
        }

    monkeypatch.setattr(
        evaluate_answers_with_judge,
        "evaluate_case",
        fake_evaluate_case,
    )

    summary = evaluate_answers_with_judge.run_evaluation(
        case_limit=1,
        cases=[
            {
                "id": "custom_case_one",
                "question": "Custom question one?",
            },
            {
                "id": "custom_case_two",
                "question": "Custom question two?",
            },
        ],
    )

    assert summary["case_source"] == "custom"
    assert summary["total"] == 1
    assert evaluated_case_ids == ["custom_case_one"]
