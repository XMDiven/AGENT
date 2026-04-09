# Markdown RAG FastAPI MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a minimal FastAPI Markdown RAG pipeline that indexes local Markdown files into Qdrant and serves `POST /ask` responses with `answer + sources`.

**Architecture:** Keep ingestion offline in a script and expose only a single FastAPI question-answering endpoint. Reuse the existing `ingestion`, `retrieval`, `generation`, and `infrastructure` modules, with `services` orchestrating the application flow and `app` owning the HTTP boundary.

**Tech Stack:** Python 3.11+, FastAPI, Pydantic v2, LangChain, Qdrant, stdlib `unittest`

---

## File Map

- Modify: `config/config.py`
  Add `RAW_MARKDOWN_DIR`, `SOURCE_SNIPPET_LENGTH`, and `APP_TITLE` configuration constants used by the MVP flow.
- Modify: `src/ingestion/loaders/markdown_loader.py`
  Replace the current loader with a dependency-free UTF-8 Markdown reader.
- Modify: `src/services/ingest_service.py`
  Implement single-file Markdown ingestion orchestration and return typed summary counts.
- Modify: `src/infrastructure/vectore_store.py`
  Make chunk ingestion create or reuse the target collection safely on the first run.
- Modify: `src/scripts/build_index.py`
  Scan Markdown files under the configured raw directory and aggregate indexing totals.
- Modify: `src/generation/context_formatter.py`
  Produce stable numbered context blocks for the answer prompt.
- Modify: `src/services/ask_service.py`
  Implement retrieval, fallback handling, answer generation, and source assembly.
- Modify: `src/schemas/ask_schema.py`
  Define the `AskRequest` Pydantic request model.
- Modify: `src/schemas/answer_schema.py`
  Define `SourceItem` and `AnswerResponse`.
- Modify: `app/routers/ask.py`
  Expose `POST /ask` and translate service failures into HTTP 500.
- Modify: `app/routers/health.py`
  Expose `GET /health` for basic service checks.
- Modify: `app/main.py`
  Create the FastAPI application and register routers.
- Create: `tests/test_ingest_service.py`
  Verify Markdown loading plus ingestion orchestration without touching real Qdrant.
- Create: `tests/test_vector_store.py`
  Verify first-run chunk ingestion uses `from_documents` to create or reuse the target collection.
- Create: `tests/test_build_index.py`
  Verify Markdown file discovery and aggregated indexing counts.
- Create: `tests/test_ask_service.py`
  Verify fallback behavior, context formatting, and source assembly.
- Create: `tests/test_api.py`
  Verify `/ask` success and validation behavior plus `/health`.
- Create: `tests/fixtures/markdown/sample_rag.md`
  Provide a deterministic sample Markdown document for manual smoke testing.

### Task 1: Implement The Ingestion Service

**Files:**
- Modify: `config/config.py`
- Modify: `src/ingestion/loaders/markdown_loader.py`
- Modify: `src/services/ingest_service.py`
- Test: `tests/test_ingest_service.py`

- [ ] **Step 1: Write the failing ingestion service test**

```python
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from langchain_core.documents import Document

from src.ingestion.loaders.markdown_loader import load_markdown
from src.services.ingest_service import ingest_markdown_file


class IngestServiceTest(TestCase):
    """Verify Markdown ingestion orchestration."""

    def test_load_markdown_reads_utf8_markdown_file(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "sample.md"
            path.write_text("# Title\n\nBody", encoding="utf-8")

            documents = load_markdown(path)

        self.assertEqual(len(documents), 1)
        self.assertEqual(documents[0].page_content, "# Title\n\nBody")
        self.assertEqual(documents[0].metadata["source"], str(path))

    @patch("src.services.ingest_service.ingest_chunks")
    @patch("src.services.ingest_service.chunk_markdown")
    @patch("src.services.ingest_service.load_markdown")
    def test_ingest_markdown_file_returns_counts(
        self,
        mock_load_markdown,
        mock_chunk_markdown,
        mock_ingest_chunks,
    ) -> None:
        document = Document(
            page_content="# Intro\n\nLangChain is a framework.",
            metadata={"source": "data/raw/sample_rag.md"},
        )
        chunk = Document(
            page_content="LangChain is a framework.",
            metadata={
                "source": "data/raw/sample_rag.md",
                "section_path": "Intro",
            },
        )

        mock_load_markdown.return_value = [document]
        mock_chunk_markdown.return_value = [chunk]
        mock_ingest_chunks.return_value = ["chunk-1"]

        result = ingest_markdown_file(Path("data/raw/sample_rag.md"))

        self.assertEqual(result["path"], "data/raw/sample_rag.md")
        self.assertEqual(result["documents"], 1)
        self.assertEqual(result["chunks"], 1)
        self.assertEqual(result["stored"], 1)
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
conda run -n AI_DEV python -m unittest tests.test_ingest_service -v
```

Expected:

```text
ERROR: tests.test_ingest_service ...
ModuleNotFoundError or ImportError from the current Markdown loader implementation
```

- [ ] **Step 3: Write the minimal ingestion implementation**

Update `config/config.py` by adding these constants near the existing retrieval configuration:

```python
RAW_MARKDOWN_DIR: str = "data/raw"
SOURCE_SNIPPET_LENGTH: int = 200
APP_TITLE: str = "Markdown RAG API"
```

Replace `src/ingestion/loaders/markdown_loader.py` with:

```python
from pathlib import Path

from langchain_core.documents import Document


def load_markdown(path: str | Path) -> list[Document]:
    """Load a single Markdown file into LangChain documents."""
    markdown_path = Path(path)
    content = markdown_path.read_text(encoding="utf-8")
    return [
        Document(
            page_content=content,
            metadata={"source": str(markdown_path)},
        )
    ]
```

Replace `src/services/ingest_service.py` with:

```python
from pathlib import Path
from typing import TypedDict

from src.ingestion.chunkers.markdown_chunker import chunk_markdown
from src.ingestion.loaders.markdown_loader import load_markdown
from src.infrastructure.vectore_store import ingest_chunks


class IngestResult(TypedDict):
    """Summary of a single Markdown ingestion run."""

    path: str
    documents: int
    chunks: int
    stored: int


def ingest_markdown_file(path: str | Path) -> IngestResult:
    """Load, chunk, and store a single Markdown file."""
    documents = load_markdown(path)
    chunks = chunk_markdown(documents)
    ids = ingest_chunks(chunks)

    return {
        "path": str(path),
        "documents": len(documents),
        "chunks": len(chunks),
        "stored": len(ids),
    }
```

- [ ] **Step 4: Run the test to verify it passes**

Run:

```bash
conda run -n AI_DEV python -m unittest tests.test_ingest_service -v
```

Expected:

```text
test_ingest_markdown_file_returns_counts ... ok
test_load_markdown_reads_utf8_markdown_file ... ok

----------------------------------------------------------------------
Ran 2 tests in ...

OK
```

- [ ] **Step 5: Commit**

```bash
git add config/config.py src/ingestion/loaders/markdown_loader.py src/services/ingest_service.py tests/test_ingest_service.py
git commit -m "feat: add markdown ingestion service"
```

### Task 2: Make Vector Store Ingestion Safe On First Run

**Files:**
- Modify: `src/infrastructure/vectore_store.py`
- Test: `tests/test_vector_store.py`

- [ ] **Step 1: Write the failing vector-store test**

```python
from unittest import TestCase
from unittest.mock import patch

from langchain_core.documents import Document

from config import config
from src.infrastructure.vectore_store import ingest_chunks


class VectorStoreTest(TestCase):
    """Verify first-run Qdrant ingestion setup."""

    def test_ingest_chunks_returns_empty_list_for_no_chunks(self) -> None:
        self.assertEqual(ingest_chunks([]), [])

    @patch("src.infrastructure.vectore_store.uuid.uuid4", side_effect=["id-1"])
    @patch("src.infrastructure.vectore_store.QdrantVectorStore.from_documents")
    @patch("src.infrastructure.vectore_store.get_embeddings")
    @patch("src.infrastructure.vectore_store.os.getenv", return_value="http://localhost:6333")
    def test_ingest_chunks_uses_from_documents_for_first_write(
        self,
        mock_getenv,
        mock_get_embeddings,
        mock_from_documents,
        mock_uuid4,
    ) -> None:
        chunks = [
            Document(
                page_content="LangChain is a framework.",
                metadata={"source": "data/raw/sample_rag.md"},
            )
        ]

        ids = ingest_chunks(chunks)

        self.assertEqual(ids, ["id-1"])
        mock_get_embeddings.assert_called_once()
        mock_from_documents.assert_called_once()
        _, kwargs = mock_from_documents.call_args
        self.assertEqual(kwargs["collection_name"], config.COLLECTION_NAME)
        self.assertEqual(kwargs["url"], "http://localhost:6333")
        self.assertEqual(kwargs["ids"], ["id-1"])
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
conda run -n AI_DEV python -m unittest tests.test_vector_store -v
```

Expected:

```text
FAIL: test_ingest_chunks_uses_from_documents_for_first_write ...
AssertionError: Expected 'from_documents' to have been called once
```

- [ ] **Step 3: Write the minimal vector-store implementation**

Replace `src/infrastructure/vectore_store.py` with:

```python
import os
import uuid

import dotenv
from langchain_core.documents import Document
from langchain_qdrant import QdrantVectorStore

from config import config
from src.infrastructure.embedding_client import get_embeddings

dotenv.load_dotenv()


def get_vector_store() -> QdrantVectorStore:
    """Return a LangChain Qdrant vector store bound to an existing collection."""
    qdrant_url = os.getenv("QDRANT_URL")
    if not qdrant_url:
        raise RuntimeError("QDRANT_URL is not set")

    return QdrantVectorStore.from_existing_collection(
        embedding=get_embeddings(),
        collection_name=config.COLLECTION_NAME,
        url=qdrant_url,
    )


def ingest_chunks(chunks: list[Document]) -> list[str]:
    """Embed chunk documents and store them in Qdrant."""
    if not chunks:
        return []

    qdrant_url = os.getenv("QDRANT_URL")
    if not qdrant_url:
        raise RuntimeError("QDRANT_URL is not set")

    ids = [str(uuid.uuid4()) for _ in chunks]
    QdrantVectorStore.from_documents(
        documents=chunks,
        embedding=get_embeddings(),
        ids=ids,
        collection_name=config.COLLECTION_NAME,
        url=qdrant_url,
    )
    return ids
```

- [ ] **Step 4: Run the test to verify it passes**

Run:

```bash
conda run -n AI_DEV python -m unittest tests.test_vector_store -v
```

Expected:

```text
test_ingest_chunks_returns_empty_list_for_no_chunks ... ok
test_ingest_chunks_uses_from_documents_for_first_write ... ok

----------------------------------------------------------------------
Ran 2 tests in ...

OK
```

- [ ] **Step 5: Commit**

```bash
git add src/infrastructure/vectore_store.py tests/test_vector_store.py
git commit -m "feat: support first-run qdrant ingestion"
```

### Task 3: Build The Markdown Index Script

**Files:**
- Modify: `src/scripts/build_index.py`
- Create: `tests/fixtures/markdown/sample_rag.md`
- Test: `tests/test_build_index.py`

- [ ] **Step 1: Write the failing build-index test**

```python
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from src.scripts.build_index import build_index


class BuildIndexTest(TestCase):
    """Verify Markdown discovery for index building."""

    @patch("src.scripts.build_index.ingest_markdown_file")
    def test_build_index_processes_only_markdown_files(
        self,
        mock_ingest_markdown_file,
    ) -> None:
        mock_ingest_markdown_file.side_effect = [
            {"path": "a.md", "documents": 1, "chunks": 2, "stored": 2},
            {"path": "nested/b.md", "documents": 1, "chunks": 3, "stored": 3},
        ]

        with TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "a.md").write_text("# A\n\nAlpha", encoding="utf-8")
            (root / "ignore.txt").write_text("ignore", encoding="utf-8")
            (root / "nested").mkdir()
            (root / "nested" / "b.md").write_text("# B\n\nBeta", encoding="utf-8")

            summary = build_index(root)

        self.assertEqual(summary["files"], 2)
        self.assertEqual(summary["chunks"], 5)
        self.assertEqual(summary["stored"], 5)
        self.assertEqual(mock_ingest_markdown_file.call_count, 2)
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
conda run -n AI_DEV python -m unittest tests.test_build_index -v
```

Expected:

```text
ERROR: tests.test_build_index ...
ImportError: cannot import name 'build_index'
```

- [ ] **Step 3: Write the minimal build-index implementation**

Replace `src/scripts/build_index.py` with:

```python
from pathlib import Path
from typing import TypedDict

from config import config
from src.services.ingest_service import ingest_markdown_file


class BuildIndexSummary(TypedDict):
    """Summary of a full Markdown indexing run."""

    files: int
    chunks: int
    stored: int


def build_index(data_dir: str | Path = config.RAW_MARKDOWN_DIR) -> BuildIndexSummary:
    """Index all Markdown files under the configured raw directory."""
    data_path = Path(data_dir)
    markdown_files = sorted(data_path.rglob("*.md"))
    summary: BuildIndexSummary = {"files": 0, "chunks": 0, "stored": 0}

    for markdown_file in markdown_files:
        result = ingest_markdown_file(markdown_file)
        summary["files"] += 1
        summary["chunks"] += result["chunks"]
        summary["stored"] += result["stored"]

    return summary


def main() -> None:
    """Build the Markdown vector index from local files."""
    summary = build_index()
    print(
        f"Indexed {summary['files']} markdown files into "
        f"{summary['stored']} vectors across {summary['chunks']} chunks."
    )


if __name__ == "__main__":
    main()
```

Create `tests/fixtures/markdown/sample_rag.md` with:

```markdown
# LangChain

## Overview

LangChain is a framework for building applications with language models.

## Retrieval

Retrieval augmented generation combines search with generation.
```

- [ ] **Step 4: Run the test to verify it passes**

Run:

```bash
conda run -n AI_DEV python -m unittest tests.test_build_index -v
```

Expected:

```text
test_build_index_processes_only_markdown_files ... ok

----------------------------------------------------------------------
Ran 1 test in ...

OK
```

- [ ] **Step 5: Commit**

```bash
git add src/scripts/build_index.py tests/test_build_index.py tests/fixtures/markdown/sample_rag.md
git commit -m "feat: add markdown build index script"
```

### Task 4: Implement Answer Schemas And Ask Service

**Files:**
- Modify: `src/schemas/ask_schema.py`
- Modify: `src/schemas/answer_schema.py`
- Modify: `src/generation/context_formatter.py`
- Modify: `src/services/ask_service.py`
- Test: `tests/test_ask_service.py`

- [ ] **Step 1: Write the failing ask-service test**

```python
from unittest import TestCase
from unittest.mock import patch

from langchain_core.documents import Document

from config import config
from src.services.ask_service import ask_question


class AskServiceTest(TestCase):
    """Verify Markdown RAG answer orchestration."""

    @patch("src.services.ask_service.get_retriever")
    def test_ask_question_returns_fallback_when_no_documents(
        self,
        mock_get_retriever,
    ) -> None:
        mock_get_retriever.return_value.invoke.return_value = []

        response = ask_question("未知问题")

        self.assertEqual(response.answer, config.FALLBACK_ANSWER)
        self.assertEqual(response.sources, [])

    @patch("src.services.ask_service.generate_answer")
    @patch("src.services.ask_service.get_qa_prompt")
    @patch("src.services.ask_service.get_client")
    @patch("src.services.ask_service.get_retriever")
    def test_ask_question_returns_answer_and_sources(
        self,
        mock_get_retriever,
        mock_get_client,
        mock_get_qa_prompt,
        mock_generate_answer,
    ) -> None:
        documents = [
            Document(
                page_content="LangChain is a framework.",
                metadata={
                    "source": "data/raw/sample_rag.md",
                    "section_path": "LangChain > Overview",
                },
            )
        ]
        mock_get_retriever.return_value.invoke.return_value = documents
        mock_get_client.return_value = object()
        mock_get_qa_prompt.return_value = object()
        mock_generate_answer.return_value = "LangChain 是一个框架。"

        response = ask_question("LangChain 是什么？")

        self.assertEqual(response.answer, "LangChain 是一个框架。")
        self.assertEqual(len(response.sources), 1)
        self.assertEqual(response.sources[0].source, "data/raw/sample_rag.md")
        self.assertEqual(
            response.sources[0].section_path,
            "LangChain > Overview",
        )
        self.assertEqual(
            response.sources[0].snippet,
            "LangChain is a framework.",
        )

        _, kwargs = mock_generate_answer.call_args
        self.assertIn("[1]", kwargs["context"])
        self.assertIn("source: data/raw/sample_rag.md", kwargs["context"])
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
conda run -n AI_DEV python -m unittest tests.test_ask_service -v
```

Expected:

```text
ERROR: tests.test_ask_service ...
AttributeError: 'NoneType' object has no attribute 'answer'
```

- [ ] **Step 3: Write the minimal ask-service implementation**

Replace `src/schemas/ask_schema.py` with:

```python
from pydantic import BaseModel, ConfigDict, Field


class AskRequest(BaseModel):
    """Request body for the ask endpoint."""

    model_config = ConfigDict(str_strip_whitespace=True)

    question: str = Field(min_length=1)
```

Replace `src/schemas/answer_schema.py` with:

```python
from pydantic import BaseModel


class SourceItem(BaseModel):
    """Source citation returned with an answer."""

    source: str
    section_path: str
    snippet: str


class AnswerResponse(BaseModel):
    """Answer payload returned by the ask endpoint."""

    answer: str
    sources: list[SourceItem]
```

Replace `src/generation/context_formatter.py` with:

```python
from langchain_core.documents import Document


def format_context(documents: list[Document]) -> str:
    """Format retrieved documents into a prompt context string."""
    blocks: list[str] = []

    for index, doc in enumerate(documents, start=1):
        source = str(doc.metadata.get("source") or "unknown")
        section_path = str(doc.metadata.get("section_path") or "unknown")
        blocks.append(
            f"[{index}]\n"
            f"source: {source}\n"
            f"section_path: {section_path}\n"
            f"content: {doc.page_content}"
        )

    return "\n\n".join(blocks)
```

Replace `src/services/ask_service.py` with:

```python
from langchain_core.documents import Document

from config import config
from src.generation.answer_generator import generate_answer
from src.generation.context_formatter import format_context
from src.generation.qa_prompt import get_qa_prompt
from src.infrastructure.llm_client import get_client
from src.retrieval.retriever import get_retriever
from src.schemas.answer_schema import AnswerResponse, SourceItem


def build_sources(documents: list[Document]) -> list[SourceItem]:
    """Convert retrieved documents into response source items."""
    sources: list[SourceItem] = []

    for doc in documents:
        source = str(doc.metadata.get("source") or "unknown")
        section_path = str(doc.metadata.get("section_path") or "unknown")
        snippet = doc.page_content.strip()[: config.SOURCE_SNIPPET_LENGTH]
        sources.append(
            SourceItem(
                source=source,
                section_path=section_path,
                snippet=snippet,
            )
        )

    return sources


def ask_question(question: str) -> AnswerResponse:
    """Answer a user question with Markdown RAG."""
    retriever = get_retriever()
    documents: list[Document] = retriever.invoke(question)

    if not documents:
        return AnswerResponse(
            answer=config.FALLBACK_ANSWER,
            sources=[],
        )

    context = format_context(documents)
    answer = generate_answer(
        question=question,
        context=context,
        llm=get_client(),
        prompt=get_qa_prompt(),
    )

    return AnswerResponse(
        answer=answer,
        sources=build_sources(documents),
    )
```

- [ ] **Step 4: Run the test to verify it passes**

Run:

```bash
conda run -n AI_DEV python -m unittest tests.test_ask_service -v
```

Expected:

```text
test_ask_question_returns_answer_and_sources ... ok
test_ask_question_returns_fallback_when_no_documents ... ok

----------------------------------------------------------------------
Ran 2 tests in ...

OK
```

- [ ] **Step 5: Commit**

```bash
git add src/schemas/ask_schema.py src/schemas/answer_schema.py src/generation/context_formatter.py src/services/ask_service.py tests/test_ask_service.py
git commit -m "feat: add markdown ask service"
```

### Task 5: Expose The FastAPI API

**Files:**
- Modify: `app/routers/ask.py`
- Modify: `app/routers/health.py`
- Modify: `app/main.py`
- Test: `tests/test_api.py`

- [ ] **Step 1: Write the failing API test**

```python
from unittest import TestCase
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from src.schemas.answer_schema import AnswerResponse, SourceItem


class ApiTest(TestCase):
    """Verify FastAPI routes for the Markdown RAG MVP."""

    @patch("app.routers.ask.ask_question")
    def test_post_ask_returns_answer_payload(
        self,
        mock_ask_question,
    ) -> None:
        mock_ask_question.return_value = AnswerResponse(
            answer="LangChain 是一个框架。",
            sources=[
                SourceItem(
                    source="data/raw/sample_rag.md",
                    section_path="LangChain > Overview",
                    snippet="LangChain is a framework.",
                )
            ],
        )

        client = TestClient(app)
        response = client.post(
            "/ask",
            json={"question": "LangChain 是什么？"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["answer"], "LangChain 是一个框架。")
        self.assertEqual(
            response.json()["sources"][0]["source"],
            "data/raw/sample_rag.md",
        )

    def test_post_ask_returns_422_for_invalid_payload(self) -> None:
        client = TestClient(app)

        response = client.post("/ask", json={})

        self.assertEqual(response.status_code, 422)

    def test_get_health_returns_ok(self) -> None:
        client = TestClient(app)

        response = client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
conda run -n AI_DEV python -m unittest tests.test_api -v
```

Expected:

```text
ERROR: tests.test_api ...
ImportError: cannot import name 'app'
```

- [ ] **Step 3: Write the minimal FastAPI implementation**

Replace `app/routers/ask.py` with:

```python
from fastapi import APIRouter, HTTPException

from src.schemas.answer_schema import AnswerResponse
from src.schemas.ask_schema import AskRequest
from src.services.ask_service import ask_question

router = APIRouter()


@router.post("/ask", response_model=AnswerResponse)
def ask(request: AskRequest) -> AnswerResponse:
    """Answer a user question with Markdown RAG."""
    try:
        return ask_question(request.question)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Failed to answer question",
        ) from exc
```

Replace `app/routers/health.py` with:

```python
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health_check() -> dict[str, str]:
    """Return a basic health status."""
    return {"status": "ok"}
```

Replace `app/main.py` with:

```python
from fastapi import FastAPI

from app.routers.ask import router as ask_router
from app.routers.health import router as health_router
from config import config


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(title=config.APP_TITLE)
    app.include_router(ask_router)
    app.include_router(health_router)
    return app


app = create_app()
```

- [ ] **Step 4: Run the test to verify it passes**

Run:

```bash
conda run -n AI_DEV python -m unittest tests.test_api -v
```

Expected:

```text
test_get_health_returns_ok ... ok
test_post_ask_returns_422_for_invalid_payload ... ok
test_post_ask_returns_answer_payload ... ok

----------------------------------------------------------------------
Ran 3 tests in ...

OK
```

- [ ] **Step 5: Commit**

```bash
git add app/routers/ask.py app/routers/health.py app/main.py tests/test_api.py
git commit -m "feat: add markdown rag api routes"
```

## End-To-End Verification

After Task 5 passes, run the full smoke flow in order.

### 1. Run the full automated test suite

```bash
conda run -n AI_DEV python -m unittest \
  tests.test_ingest_service \
  tests.test_vector_store \
  tests.test_build_index \
  tests.test_ask_service \
  tests.test_api \
  -v
```

Expected:

```text
Ran 10 tests in ...

OK
```

### 2. Copy the sample Markdown file into the raw data directory if you do not already have a `.md` file there

```bash
cp tests/fixtures/markdown/sample_rag.md data/raw/sample_rag.md
```

Expected:

```text
No output
```

### 3. Build the vector index

```bash
conda run -n AI_DEV python src/scripts/build_index.py
```

Expected:

```text
Indexed 1 markdown files into ... vectors across ... chunks.
```

### 4. Start the FastAPI app

```bash
conda run -n AI_DEV uvicorn app.main:app --reload
```

Expected:

```text
Uvicorn running on http://127.0.0.1:8000
```

### 5. Verify the health route from another terminal

```bash
curl -s http://127.0.0.1:8000/health
```

Expected:

```json
{"status":"ok"}
```

### 6. Verify the ask route from another terminal

```bash
curl -s \
  -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"LangChain 是什么？"}'
```

Expected:

```json
{
  "answer": "LangChain 是一个用于构建语言模型应用的框架。",
  "sources": [
    {
      "source": "data/raw/sample_rag.md",
      "section_path": "LangChain > Overview",
      "snippet": "LangChain is a framework for building applications with language models."
    }
  ]
}
```

## Self-Review

- Spec coverage check:
  - Offline Markdown indexing is covered by Task 1, Task 2, and Task 3.
  - `POST /ask` with `answer + sources` is covered by Task 4 and Task 5.
  - Fallback behavior is covered by Task 4 tests.
  - FastAPI exposure and health checks are covered by Task 5.
  - Manual and automated verification are covered by the End-To-End Verification section.
- Placeholder scan:
  - No `TODO`, `TBD`, or deferred “implement later” steps remain.
- Type consistency:
  - `AskRequest`, `SourceItem`, `AnswerResponse`, `IngestResult`, and `BuildIndexSummary` are defined before later tasks rely on them.
