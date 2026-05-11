from rag_app.scripts import evaluate_answers, evaluate_retrieval


def main() -> None:
    evaluate_retrieval.main()
    evaluate_answers.main()


if __name__ == "__main__":
    main()
