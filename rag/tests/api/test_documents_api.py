from rag_app.config import config


def test_upload_markdown_document(client, tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(config, "RAW_DATA_DIR", tmp_path)
    monkeypatch.setattr(config, "PROJECT_ROOT", tmp_path.parent)

    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "example.md",
                b"# Example\n\nHello RAG",
                "text/markdown",
            )
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "filename": "example.md",
        "saved_path": "example.md",
        "content_type": "text/markdown",
    }
    assert (tmp_path / "example.md").read_bytes() == b"# Example\n\nHello RAG"


def test_upload_rejects_unsupported_file_type(client, tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(config, "RAW_DATA_DIR", tmp_path)
    monkeypatch.setattr(config, "PROJECT_ROOT", tmp_path.parent)

    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "example.txt",
                b"not supported",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Only .md and .pdf files are supported"
    }


def test_upload_uses_safe_filename(client, tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(config, "RAW_DATA_DIR", tmp_path)

    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "../example.md",
                b"# Safe filename",
                "text/markdown",
            )
        },
    )

    assert response.status_code == 200
    assert response.json()["filename"] == "example.md"
    assert response.json()["saved_path"] == "example.md"
    assert (tmp_path / "example.md").read_bytes() == b"# Safe filename"
    assert not (tmp_path.parent / "example.md").exists()
