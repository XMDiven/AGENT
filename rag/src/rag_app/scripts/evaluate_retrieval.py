from __future__ import annotations

import json
from pathlib import Path
from dataclasses import dataclass

from langchain_core.documents import Document

from rag_app.retrieval.retriever import get_retriever

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CASES_PATH = PROJECT_ROOT / "experiments" / "retrieval_eval_cases.json"

@dataclass(frozen=True)
class RetrievalEvalCase:
    id : str
    question : str
    expected_source_contains:list[str]
    match : str = "any"
def load_case(path : Path = DEFAULT_CASES_PATH) ->list[RetrievalEvalCase]:
    raw_cases = json.loads(path.read_text(encoding="utf-8"))

    return [
        RetrievalEvalCase(
            id = case["id"],
            question=case["question"],
            expected_source_contains=case["expected_source_contains"],
            match=case.get("match", "any"),
        )
        for case in raw_cases
    ]

def get_sources(documents : list[Document]) -> list[str]:
    return [
        document.metadata.get("source" , "")
        for document in documents
    ]



def has_expected_sources(
        sources : list[str] ,
        expected_source_contains: list[str],
        match : str = "any"
) -> bool:
    normalize_sources = [source.lower() for source in sources]
    normalize_expected = [expected.lower() for expected in expected_source_contains]

    if match == "any":
        return any(
            expected in source
            for source in normalize_sources
            for expected in normalize_expected
        )

    if match == "all":
        return all(
            any(expected in source for source in normalize_sources)
            for expected in normalize_expected
        )

    raise ValueError(f"Unsupported match mode: {match}")


def evaluate_case(case:RetrievalEvalCase , documents: list[Document]) -> bool:

    sources = get_sources(documents)

    passed = has_expected_sources(
        sources ,
        case.expected_source_contains,
        case.match
    )

    status = "PASS" if passed else "FAIL"

    print(f"Evaluating {case.id} with {status}")
    print(f"question: {case.question}")
    print(f"expected_source_contains: {case.expected_source_contains}")
    print("retrieved sources:")

    for source in sources:
        print(f"- {source}")

    print()

    return passed
def main():
    cases = load_case()
    retriever = get_retriever()
    results = []
    for case in cases:
        documents = retriever.invoke(case.question)
        passed = evaluate_case(case, documents)
        results.append(passed)
    passed_count = sum(results)
    total_count = len(results)

    print(f"summary: {passed_count}/{total_count} passed")

    if passed_count != total_count:
        raise SystemExit(1)

if "__main__" == __name__:
    main()
