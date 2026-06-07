from langchain_openai import ChatOpenAI

from rag_app.config import config


def get_client() -> ChatOpenAI:
    base_url = config.settings.llm_base_url
    model = config.settings.llm_model_id
    api_key = config.settings.llm_api_key

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
