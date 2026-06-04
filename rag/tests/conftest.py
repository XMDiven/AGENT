from collections.abc import Iterator
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from rag_app.app import main as app_main
from rag_app.infrastructure.resources import AppResources


@pytest.fixture
def app_resources() -> AppResources:
    return AppResources(
        llm_client=Mock(),
        vector_store=Mock(),
    )


@pytest.fixture
def client(
    monkeypatch: pytest.MonkeyPatch,
    app_resources: AppResources,
) -> Iterator[TestClient]:
    monkeypatch.setattr(
        app_main,
        "create_app_resources",
        lambda: app_resources,
    )

    with TestClient(app_main.app) as client:
        yield client
