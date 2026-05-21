import argparse
import json
from dataclasses import asdict

from agent_app.service import run_agent


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the lightweight Agent orchestration flow.",
    )
    parser.add_argument("question")
    args = parser.parse_args()

    result = run_agent(args.question)

    print(
        json.dumps(
            asdict(result),
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
