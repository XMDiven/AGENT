from langchain_ollama import OllamaEmbeddings

from rag_app.config import config


def get_embeddings() -> OllamaEmbeddings:
    base_url = config.settings.embedding_base_url
    model = config.settings.embedding_model

    if not base_url:
        raise RuntimeError("EMBEDDING_BASE_URL is not set")

    if not model:
        raise RuntimeError("EMBEDDING_MODEL is not set")

    return OllamaEmbeddings(
        base_url=base_url,
        model=model,
    )
