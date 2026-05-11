from collections.abc import Iterator
import pytest
from fastapi.testclient import TestClient
from rag_app.app.main import app
@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as client:
        yield client
