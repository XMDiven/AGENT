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


def test_upload_batch_documents(client, tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(config, "RAW_DATA_DIR", tmp_path)

    response = client.post(
        "/documents/upload/batch",
        files=[
            (
                "files",
                (
                    "one.md",
                    b"# One",
                    "text/markdown",
                ),
            ),
            (
                "files",
                (
                    "two.pdf",
                    b"%PDF-1.4",
                    "application/pdf",
                ),
            ),
        ],
    )

    assert response.status_code == 200
    assert response.json() == {
        "files": [
            {
                "filename": "one.md",
                "saved_path": "one.md",
                "content_type": "text/markdown",
            },
            {
                "filename": "two.pdf",
                "saved_path": "two.pdf",
                "content_type": "application/pdf",
            },
        ]
    }
    assert (tmp_path / "one.md").read_bytes() == b"# One"
    assert (tmp_path / "two.pdf").read_bytes() == b"%PDF-1.4"


def test_upload_batch_rejects_unsupported_file_type(
    client,
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(config, "RAW_DATA_DIR", tmp_path)

    response = client.post(
        "/documents/upload/batch",
        files=[
            (
                "files",
                (
                    "valid.md",
                    b"# Valid",
                    "text/markdown",
                ),
            ),
            (
                "files",
                (
                    "invalid.txt",
                    b"not supported",
                    "text/plain",
                ),
            ),
        ],
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Only .md and .pdf files are supported"
    }
    assert not (tmp_path / "valid.md").exists()
    assert not (tmp_path / "invalid.txt").exists()
