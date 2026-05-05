from unittest.mock import Mock

from qdrant_client import models

from src.scripts import reset_index


def test_reset_index_deletes_all_points_from_configured_collection(
    monkeypatch,
) -> None:
    """Delete all points from the configured Qdrant collection."""
    mock_client = Mock()
    mock_qdrant_client = Mock(return_value=mock_client)

    monkeypatch.setenv("QDRANT_URL", "http://localhost:6333")
    monkeypatch.setattr(reset_index.config, "COLLECTION_NAME", "documents")
    monkeypatch.setattr(reset_index, "QdrantClient", mock_qdrant_client)

    result = reset_index.reset_index()

    assert result == {"collection": "documents", "deleted": True}
    mock_qdrant_client.assert_called_once_with(url="http://localhost:6333")
    mock_client.delete.assert_called_once_with(
        collection_name="documents",
        points_selector=models.Filter(must=[]),
        wait=True,
    )
