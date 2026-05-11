from pathlib import Path

import pytest

from rag_app.config import config
from rag_app.ingestion.loaders.markdown_loader import load_markdown


def test_load_markdown_returns_document_with_relative_source(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project_root = tmp_path
    raw_dir = project_root / "data" / "raw"
    raw_dir.mkdir(parents=True)
    md_path = raw_dir / "sample.md"

    monkeypatch.setattr(config, "PROJECT_ROOT", project_root)

    md_path.write_text("# Hello\n\nLangChain docs.", encoding="utf-8")

    documents = load_markdown(str(md_path))

    assert len(documents) == 1
    assert "LangChain" in documents[0].page_content
    assert documents[0].metadata["source"] == "data/raw/sample.md"
