import uuid
from unittest.mock import Mock

import pytest
from langchain_core.documents import Document

from src.infrastructure import vectore_store
from src.infrastructure.vectore_store import build_chunk_id, ingest_chunks


def test_build_chunk_id_returns_same_id_for_same_document() -> None:
    document = Document(
        page_content="Qdrant is a vector database.",
        metadata={"source": "data/raw/qdrant-docs.md"},
    )
    first_chunk_id = build_chunk_id(document)
    second_chunk_id = build_chunk_id(document)
    assert first_chunk_id == second_chunk_id
    assert str(uuid.UUID(first_chunk_id)) == first_chunk_id
def test_build_chunk_id_changes_for_different_content() -> None:
    first_document = Document(
        page_content="Qdrant is a vector database.",
        metadata={"source": "data/raw/qdrant-docs.md"},
    )

    second_document = Document(
        page_content="Qdrant",
        metadata={"source": "data/raw/qdrant-docs.md"},
    )
    first_chunk_id = build_chunk_id(first_document)
    second_chunk_id = build_chunk_id(second_document)
    assert first_chunk_id != second_chunk_id

def test_ingest_chunks_uses_stable_document_ids(monkeypatch : pytest.MonkeyPatch) -> None:
    document = Document(
        page_content="Qdrant is a vector database.",
        metadata={"source": "data/raw/qdrant-docs.md"},
    )

    mock_vector_store = Mock()

    monkeypatch.setattr(
        vectore_store,
        "get_vector_store",
        Mock(return_value=mock_vector_store),
    )
    ids = ingest_chunks([document])
    expected_ids = build_chunk_id(document)
    assert ids == [expected_ids]
    mock_vector_store.add_documents.assert_called_once_with(
        documents=[document],
        ids=[expected_ids],
    )

def test_ingest_chunks_deduplicates_chunks_with_same_stable_id(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first_document = Document(
        page_content="Qdrant is a vector database.",
        metadata={"source": "data/raw/qdrant-docs.md"},
    )
    second_document = Document(
        page_content="Qdrant is a vector database.",
        metadata={"source": "data/raw/qdrant-docs.md"},
    )
    mock_vector_store = Mock()

    monkeypatch.setattr(
        vectore_store,
        "get_vector_store",
        Mock(return_value=mock_vector_store),
    )

    ids = ingest_chunks([first_document, second_document])
    expected_ids = build_chunk_id(first_document)
    assert ids == [expected_ids]
    mock_vector_store.add_documents.assert_called_once_with(
        documents=[first_document],
        ids=[expected_ids],
    )









