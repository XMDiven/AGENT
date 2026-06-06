from unittest.mock import Mock

import pytest

from rag_app.config import config
from rag_app.retrieval.retriever import get_retriever


def test_get_retriever_uses_configured_mmr_by_default(monkeypatch) -> None:
    monkeypatch.setattr(config, "RETRIEVAL_SEARCH_TYPE", "mmr")
    monkeypatch.setattr(config, "RETRIEVAL_TOP_K", 7)
    monkeypatch.setattr(config, "RETRIEVAL_FETCH_K", 50)
    monkeypatch.setattr(config, "RETRIEVAL_LAMBDA_MULT", 0.3)

    vector_store = Mock()
    retriever = Mock()
    vector_store.as_retriever.return_value = retriever

    result = get_retriever(vector_store=vector_store)

    assert result is retriever
    vector_store.as_retriever.assert_called_once_with(
        search_type="mmr",
        search_kwargs={
            "k": 7,
            "fetch_k": 50,
            "lambda_mult": 0.3,
        },
    )


def test_get_retriever_ignores_mmr_defaults_for_similarity(
    monkeypatch,
) -> None:
    monkeypatch.setattr(config, "RETRIEVAL_SEARCH_TYPE", "similarity")
    monkeypatch.setattr(config, "RETRIEVAL_TOP_K", 7)
    monkeypatch.setattr(config, "RETRIEVAL_FETCH_K", 50)
    monkeypatch.setattr(config, "RETRIEVAL_LAMBDA_MULT", 0.3)

    vector_store = Mock()
    retriever = Mock()
    vector_store.as_retriever.return_value = retriever

    result = get_retriever(vector_store=vector_store)

    assert result is retriever
    vector_store.as_retriever.assert_called_once_with(
        search_type="similarity",
        search_kwargs={"k": 7},
    )


def test_get_retriever_passes_mmr_search_kwargs() -> None:
    vector_store = Mock()
    retriever = Mock()
    vector_store.as_retriever.return_value = retriever

    result = get_retriever(
        top_k=7,
        search_type="mmr",
        fetch_k=50,
        lambda_mult=0.3,
        vector_store=vector_store,
    )

    assert result is retriever
    vector_store.as_retriever.assert_called_once_with(
        search_type="mmr",
        search_kwargs={
            "k": 7,
            "fetch_k": 50,
            "lambda_mult": 0.3,
        },
    )


def test_get_retriever_rejects_mmr_kwargs_for_similarity() -> None:
    vector_store = Mock()

    with pytest.raises(ValueError, match="only supported for MMR"):
        get_retriever(
            search_type="similarity",
            fetch_k=50,
            vector_store=vector_store,
        )
