# RAG Learning Project

This repository is a learning-focused Retrieval-Augmented Generation (RAG) project built around a full backend pipeline:

```text
raw documents -> ingestion -> chunking -> embeddings -> Qdrant retrieval -> LLM answer -> cited sources
```

The project supports Markdown and PDF documents, builds a Qdrant vector index, exposes a FastAPI `/ask` endpoint, and includes lightweight evaluation scripts for both retrieval quality and final answer output quality.

## Tech Stack

- FastAPI for the HTTP API
- LangChain for document processing, retrieval, and generation orchestration
- Qdrant as the vector database
- Ollama embeddings via `langchain-ollama`
- OpenAI-compatible chat model client via `langchain-openai`
- Pytest for automated tests

## Core Features

- Ingest Markdown and PDF files from `data/raw`
- Chunk documents with stable source metadata
- Store chunks in Qdrant with deterministic chunk IDs
- Ask questions through `/ask`
- Return grounded answers with structured source citations
- Evaluate retrieval with golden source cases
- Evaluate final answer output for basic answer and source contract regressions

## Project Structure

```text
app/                 FastAPI routers and app entrypoint
config/              Runtime configuration
data/raw/            Source documents
experiments/         Retrieval and answer-quality experiment records
src/ingestion/       Loaders, chunkers, and metadata handling
src/infrastructure/  Embedding, LLM, and vector store clients
src/retrieval/       Retriever construction
src/generation/      Prompt, context formatting, and answer generation
src/services/        Application service layer
src/scripts/         Indexing and evaluation scripts
tests/               Unit and script tests
```

## Environment

Use the `AI_DEV` conda environment:

```bash
conda activate AI_DEV
```

The application expects these environment variables:

```text
QDRANT_URL
QDRANT_COLLECTION
EMBEDDING_BASE_URL
EMBEDDING_MODEL
LLM_BASE_URL
LLM_MODEL_ID
MOONSHOT_API_KEY or OPENAI_API_KEY
```

Qdrant can be started with Docker Compose:

```bash
docker compose up -d qdrant
```

## Build The Index

Reset the current Qdrant collection:

```bash
conda run -n AI_DEV python -m src.scripts.reset_index
```

Build the vector index from supported raw documents:

```bash
conda run -n AI_DEV python -m src.scripts.build_index
```

## Run The API

Start FastAPI:

```bash
conda run -n AI_DEV uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```

Ask a question:

```bash
curl -X POST http://127.0.0.1:8001/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"What does retrieval augmented generation combine?"}'
```

The response contains:

- `answer`: the generated answer with numbered citations such as `[1]`
- `sources`: structured source metadata and snippets used to support the answer

## Verification

Run the test suite:

```bash
conda run -n AI_DEV pytest tests/ -q
```

Run the unified RAG evaluation:

```bash
conda run -n AI_DEV python -m src.scripts.run_eval
```

`run_eval` performs two checks:

- Retrieval evaluation: verifies expected source documents are retrieved for golden questions.
- Answer evaluation: verifies `/ask` returns non-empty answers, valid sources, expected source hits, and does not leak source metadata into the answer text.

## Current Evaluation Baseline

The current golden set contains 8 representative questions across Markdown and PDF sources. The latest verified baseline is:

```text
pytest: 27 passed
retrieval eval: 8/8 passed
answer eval: 8/8 passed
```

## Notes

- `run_eval` assumes the Qdrant index has already been built.
- Rebuild the index after changing ingestion, chunking, embedding, or metadata behavior.
- Prompt-only changes do not require rebuilding the index.
