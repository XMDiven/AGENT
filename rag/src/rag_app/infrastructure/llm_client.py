import os

import dotenv
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()


def get_client() -> ChatOpenAI:
    base_url = os.getenv("LLM_BASE_URL")
    model = os.getenv("LLM_MODEL_ID")
    api_key = os.getenv("MOONSHOT_API_KEY") or os.getenv("OPENAI_API_KEY")

    if not base_url:
        raise RuntimeError("LLM_BASE_URL is not set")

    if not model:
        raise RuntimeError("LLM_MODEL_ID is not set")

    if not api_key:
        raise RuntimeError("MOONSHOT_API_KEY is not set")

    client = ChatOpenAI(
        api_key=api_key,
        base_url=base_url,
        model=model,
    )

    return client
