# RAG 学习项目

**语言 / Language：中文 | [English](#rag-learning-project-english)**

这是一个面向学习的 Retrieval-Augmented Generation（RAG）项目，用来探索从文档摄入到最终回答生成的完整后端链路：

```text
原始文档 -> 摄入 -> 切分 -> 向量嵌入 -> Qdrant 检索 -> LLM 生成回答 -> 引用来源
```

项目支持 Markdown 和 PDF 文档，能够构建 Qdrant 向量索引，提供 FastAPI `/ask` 问答接口，并包含轻量级评估脚本，用于检查检索质量和最终回答质量。

## 技术栈

- FastAPI：HTTP API
- LangChain：文档处理、检索和生成编排
- Qdrant：向量数据库
- `langchain-ollama`：Ollama embedding 接入
- `langchain-openai`：OpenAI 兼容聊天模型客户端
- Pytest：自动化测试

## 核心功能

- 从 `data/raw` 摄入 Markdown 和 PDF 文件
- 按稳定的来源元数据切分文档
- 使用确定性的 chunk ID 将切片写入 Qdrant
- 通过 `/ask` 接口提问
- 返回带结构化来源引用的 grounded answer
- 使用 golden source cases 评估检索结果
- 评估最终回答的基本内容、来源契约和回归风险

## 项目结构

```text
data/raw/            原始来源文档
experiments/         检索和回答质量实验记录
src/rag_app/app/                 FastAPI 路由和应用入口
src/rag_app/config/              运行时配置
src/rag_app/ingestion/           加载器、切分器和元数据处理
src/rag_app/infrastructure/      Embedding、LLM 和向量库客户端
src/rag_app/retrieval/           Retriever 构建
src/rag_app/generation/          Prompt、上下文格式化和回答生成
src/rag_app/services/            应用服务层
src/rag_app/scripts/             索引构建和评估脚本
tests/               单元测试和脚本测试
```

## 环境

使用 `AI_DEV` conda 环境：

```bash
conda activate AI_DEV
```

应用需要以下环境变量：

```text
QDRANT_URL
QDRANT_COLLECTION
EMBEDDING_BASE_URL
EMBEDDING_MODEL
LLM_BASE_URL
LLM_MODEL_ID
MOONSHOT_API_KEY or OPENAI_API_KEY
```

可以通过 Docker Compose 启动 Qdrant：

```bash
docker compose up -d qdrant
```

## 快速开始

1. 创建并激活 Python 环境：

```bash
conda create -n AI_DEV python=3.11 -y
conda activate AI_DEV
pip install -r requirements-dev.txt
pip install -e . --no-deps
```

2. 配置环境变量：

```bash
cp .env.example .env
```

根据你的 Qdrant、embedding 模型和 LLM 服务配置编辑 `.env`。不要提交真实 API key。

3. 准备语料：

把需要入库的 Markdown 或 PDF 文件放到 `data/raw/`：

```text
data/raw/
  example.md
  example.pdf
```

4. 启动 Qdrant 并构建索引：

```bash
docker compose up -d qdrant
python -m rag_app.scripts.reset_index
python -m rag_app.scripts.build_index
```

5. 启动 API 并提问：

```bash
uvicorn rag_app.app.main:app --host 127.0.0.1 --port 8001 --reload
```

```bash
curl -X POST http://127.0.0.1:8001/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"What does retrieval augmented generation combine?"}'
```

6. 运行验证：

```bash
pytest tests/ -q
python -m rag_app.scripts.run_eval
```

说明：`run_eval` 依赖已经构建好的 Qdrant 索引和本地实验语料。若你使用自己的文档，需要同步调整 `experiments/retrieval_eval_cases.json`。

## 构建索引

重置当前 Qdrant collection：

```bash
conda run -n AI_DEV python -m rag_app.scripts.reset_index
```

从支持的原始文档构建向量索引：

```bash
conda run -n AI_DEV python -m rag_app.scripts.build_index
```

## 运行 API

启动 FastAPI：

```bash
conda run -n AI_DEV uvicorn rag_app.app.main:app --host 127.0.0.1 --port 8001 --reload
```

发送问题：

```bash
curl -X POST http://127.0.0.1:8001/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"What does retrieval augmented generation combine?"}'
```

响应包含：

- `answer`：带编号引用的生成回答，例如 `[1]`
- `sources`：用于支撑回答的结构化来源元数据和片段
- `trace`：问题分析、检索和生成步骤的轻量执行轨迹

示例响应：

```json
{
  "answer": "RAG combines retrieval with generation so the model can answer using external context. [1]",
  "sources": [
    {
      "source": "data/raw/rag-paper.pdf",
      "section_path": "unknown",
      "snippet": "Retrieval-Augmented Generation combines a retriever with a generator..."
    }
  ],
  "trace": [
    {
      "step": "query_analysis",
      "status": "completed",
      "detail": {
        "normalized_question": "What does retrieval augmented generation combine?",
        "needs_retrieval": true,
        "reason": "normal knowledge question, use retrieval"
      }
    },
    {
      "step": "retrieval",
      "status": "completed",
      "detail": {
        "top_k": 7,
        "document_count": 5,
        "retrieved_sources": [
          "data/raw/rag-paper.pdf"
        ]
      }
    },
    {
      "step": "generate_answer",
      "status": "completed",
      "detail": {}
    }
  ]
}
```

## 验证

运行测试套件：

```bash
conda run -n AI_DEV pytest tests/ -q
```

运行统一 RAG 评估：

```bash
conda run -n AI_DEV python -m rag_app.scripts.run_eval
```

`run_eval` 会执行两类检查：

- 检索评估：验证 golden questions 是否检索到预期来源文档。
- 回答评估：验证 `/ask` 返回非空回答、有效来源、预期来源命中，并且不会把来源元数据泄漏到回答文本中。

## 当前评估基线

当前 golden set 包含 11 个覆盖 Markdown、PDF、中文转述和多来源对比的代表性问题。
当前已验证检索配置为 `RETRIEVAL_TOP_K = 7`。最近一次已验证基线为：

```text
pytest: 31 passed
retrieval eval: 11/11 passed
answer eval: 11/11 passed
```

## 说明

- `run_eval` 假设 Qdrant 索引已经构建完成。
- 修改 ingestion、chunking、embedding 或 metadata 行为后，需要重新构建索引。
- 只修改 prompt 时，不需要重新构建索引。

---

# RAG Learning Project (English)

**Language / 语言：[中文](#rag-学习项目) | English**

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
data/raw/            Source documents
experiments/         Retrieval and answer-quality experiment records
src/rag_app/app/                 FastAPI routers and app entrypoint
src/rag_app/config/              Runtime configuration
src/rag_app/ingestion/           Loaders, chunkers, and metadata handling
src/rag_app/infrastructure/      Embedding, LLM, and vector store clients
src/rag_app/retrieval/           Retriever construction
src/rag_app/generation/          Prompt, context formatting, and answer generation
src/rag_app/services/            Application service layer
src/rag_app/scripts/             Indexing and evaluation scripts
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

## Quickstart

1. Create and activate the Python environment:

```bash
conda create -n AI_DEV python=3.11 -y
conda activate AI_DEV
pip install -r requirements-dev.txt
pip install -e . --no-deps
```

2. Configure environment variables:

```bash
cp .env.example .env
```

Edit `.env` for your Qdrant, embedding model, and LLM service settings. Do not commit real API keys.

3. Prepare source documents:

Put Markdown or PDF files into `data/raw/`:

```text
data/raw/
  example.md
  example.pdf
```

4. Start Qdrant and build the index:

```bash
docker compose up -d qdrant
python -m rag_app.scripts.reset_index
python -m rag_app.scripts.build_index
```

5. Start the API and ask a question:

```bash
uvicorn rag_app.app.main:app --host 127.0.0.1 --port 8001 --reload
```

```bash
curl -X POST http://127.0.0.1:8001/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"What does retrieval augmented generation combine?"}'
```

6. Run verification:

```bash
pytest tests/ -q
python -m rag_app.scripts.run_eval
```

Note: `run_eval` depends on a built Qdrant index and the local experiment corpus. If you use your own documents, update `experiments/retrieval_eval_cases.json` accordingly.

## Build The Index

Reset the current Qdrant collection:

```bash
conda run -n AI_DEV python -m rag_app.scripts.reset_index
```

Build the vector index from supported raw documents:

```bash
conda run -n AI_DEV python -m rag_app.scripts.build_index
```

## Run The API

Start FastAPI:

```bash
conda run -n AI_DEV uvicorn rag_app.app.main:app --host 127.0.0.1 --port 8001 --reload
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
- `trace`: lightweight execution trace for query analysis, retrieval, and generation

Example response:

```json
{
  "answer": "RAG combines retrieval with generation so the model can answer using external context. [1]",
  "sources": [
    {
      "source": "data/raw/rag-paper.pdf",
      "section_path": "unknown",
      "snippet": "Retrieval-Augmented Generation combines a retriever with a generator..."
    }
  ],
  "trace": [
    {
      "step": "query_analysis",
      "status": "completed",
      "detail": {
        "normalized_question": "What does retrieval augmented generation combine?",
        "needs_retrieval": true,
        "reason": "normal knowledge question, use retrieval"
      }
    },
    {
      "step": "retrieval",
      "status": "completed",
      "detail": {
        "top_k": 7,
        "document_count": 5,
        "retrieved_sources": [
          "data/raw/rag-paper.pdf"
        ]
      }
    },
    {
      "step": "generate_answer",
      "status": "completed",
      "detail": {}
    }
  ]
}
```

## Verification

Run the test suite:

```bash
conda run -n AI_DEV pytest tests/ -q
```

Run the unified RAG evaluation:

```bash
conda run -n AI_DEV python -m rag_app.scripts.run_eval
```

`run_eval` performs two checks:

- Retrieval evaluation: verifies expected source documents are retrieved for golden questions.
- Answer evaluation: verifies `/ask` returns non-empty answers, valid sources, expected source hits, and does not leak source metadata into the answer text.

## Current Evaluation Baseline

The current golden set contains 11 representative questions across Markdown, PDF, Chinese paraphrase, and multi-source comparison cases.
The current verified retrieval setting is `RETRIEVAL_TOP_K = 7`. The latest verified baseline is:

```text
pytest: 31 passed
retrieval eval: 11/11 passed
answer eval: 11/11 passed
```

## Notes

- `run_eval` assumes the Qdrant index has already been built.
- Rebuild the index after changing ingestion, chunking, embedding, or metadata behavior.
- Prompt-only changes do not require rebuilding the index.
