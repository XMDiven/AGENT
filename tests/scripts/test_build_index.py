from pathlib import Path
from unittest.mock import Mock
from src.scripts.build_index import build_index

def test_build_index_aggregates_counts(monkeypatch) -> None:

    markdown_files = [
        Path("data/raw/langchain-docs.md"),
        Path("data/raw/qdrant-docs.md"),
    ]

    mock_get_markdown_files = Mock(return_value=markdown_files)
    mock_ingest_markdown_file = Mock(
        side_effect=[
            {
                "path": "data/raw/langchain-docs.md",
                "document_count": 1,
                "chunk_count": 2,
                "stored_count": 2,
            },
            {
                "path": "data/raw/qdrant-docs.md",
                "document_count": 1,
                "chunk_count": 3,
                "stored_count": 3,
            },
        ]
    )
    monkeypatch.setattr(
        "src.scripts.build_index.get_markdown_files",
        mock_get_markdown_files
    )
    monkeypatch.setattr(
        "src.scripts.build_index.ingest_markdown_file",
        mock_ingest_markdown_file
    )

    result = build_index()

    assert result == {
        "file_count": 2,
        "document_count": 2,
        "chunk_count": 5,
        "stored_count": 5,
    }

    mock_get_markdown_files.assert_called_once_with()

    assert mock_ingest_markdown_file.call_count == 2
    mock_ingest_markdown_file.assert_any_call("data/raw/langchain-docs.md")
    mock_ingest_markdown_file.assert_any_call("data/raw/qdrant-docs.md")
