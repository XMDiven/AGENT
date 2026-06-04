# End-to-End Demo

This document records a real local demo run for the RAG and lightweight Agent
projects.

## Run Metadata

- Run time: 2026-06-04 13:14:25 CST
- Repository: `/Users/mdiven/Code/Projects/AGENT`
- Conda environment: `AI_DEV`
- RAG service: `http://127.0.0.1:8001`
- Agent service: `http://127.0.0.1:8010`
- LLM model: `kimi-k2.5`
- Vector store: Qdrant, collection `documents`
- Demo file: `rag/data/raw/qdrant-docs.md`

The Agent demo used port `8010` because port `8000` was already occupied on
this machine. If port `8000` is free locally, the same request shape works with
`http://127.0.0.1:8000`.

## Preconditions

The live stack must be ready before running these commands:

```bash
cd /Users/mdiven/Code/Projects/AGENT/rag
docker compose up -d qdrant
conda run -n AI_DEV python -m rag_app.scripts.reset_index
conda run -n AI_DEV python -m rag_app.scripts.build_index
```

Start the RAG API:

```bash
cd /Users/mdiven/Code/Projects/AGENT/rag
conda run -n AI_DEV uvicorn rag_app.app.main:app --host 127.0.0.1 --port 8001
```

Start the Agent API:

```bash
cd /Users/mdiven/Code/Projects/AGENT/agent
PYTHONPATH=/Users/mdiven/Code/Projects/AGENT/agent/src:/Users/mdiven/Code/Projects/AGENT/rag/src \
  conda run -n AI_DEV uvicorn agent_app.app.main:app --host 127.0.0.1 --port 8010
```

Health checks:

```bash
curl -sS http://127.0.0.1:8001/health
curl -sS http://127.0.0.1:8010/health
```

Observed responses:

```json
{"status":"ok"}
```

```json
{"status":"ok","service":"agent"}
```

## 1. Upload Document

Command:

```bash
cd /Users/mdiven/Code/Projects/AGENT
curl -sS -X POST http://127.0.0.1:8001/documents/upload \
  -F "file=@rag/data/raw/qdrant-docs.md;type=text/markdown"
```

Observed response:

```json
{
  "filename": "qdrant-docs.md",
  "saved_path": "qdrant-docs.md",
  "content_type": "text/markdown"
}
```

## 2. Ingest Document

Command:

```bash
curl -sS -X POST http://127.0.0.1:8001/documents/ingest \
  -H "Content-Type: application/json" \
  -d '{"filename":"qdrant-docs.md"}'
```

Observed response:

```json
{
  "path": "/Users/mdiven/Code/Projects/AGENT/rag/data/raw/qdrant-docs.md",
  "document_count": 1,
  "chunk_count": 1,
  "stored_count": 1
}
```

## 3. Ask RAG

Command:

```bash
curl -sS -X POST http://127.0.0.1:8001/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"What is Qdrant used for in vector search?"}'
```

Observed response excerpt:

```json
{
  "answer": "Qdrant 是一个向量相似性搜索引擎和向量数据库，专门用于下一代 AI 应用中的语义搜索、匹配和推荐。它提供生产就绪的服务，用于存储、搜索和管理带附加载荷的向量点，支持基于神经网络或语义的匹配、分面搜索，并能将嵌入或神经网络编码器转化为完整的匹配、搜索和推荐应用...",
  "source_count": 7,
  "sources": [
    {
      "source": "data/raw/aiapp-05-qdrant-readme.md",
      "section_path": "",
      "snippet": "Vector Search Engine for the next generation of AI applications..."
    },
    {
      "source": "data/raw/qdrant-docs.md",
      "section_path": "",
      "snippet": "Qdrant Docs\nSource: https://qdrant.tech/documentation/..."
    }
  ],
  "trace": [
    {
      "step": "query_analysis",
      "status": "completed",
      "detail": {
        "question_type": "general"
      }
    },
    {
      "step": "retrieval_planning",
      "status": "completed",
      "detail": {
        "question_type": "general",
        "retrieval_strategy": "standard_retrieval",
        "top_k": 7
      }
    },
    {
      "step": "retrieval",
      "status": "completed",
      "detail": {
        "retrieval_strategy": "standard_retrieval",
        "top_k": 7,
        "duration_seconds": 0.45,
        "document_count": 7,
        "retrieved_sources": [
          "data/raw/aiapp-05-qdrant-readme.md",
          "data/raw/qdrant-docs.md"
        ]
      }
    },
    {
      "step": "generate_answer",
      "status": "completed",
      "detail": {
        "attempt": 1,
        "duration_seconds": 31.15
      }
    }
  ]
}
```

## 4. Ask RAG With Streaming

Command:

```bash
curl -sS -N -X POST http://127.0.0.1:8001/ask/stream \
  -H "Content-Type: application/json" \
  -d '{"question":"What is Qdrant used for in vector search?"}'
```

Observed NDJSON summary:

```json
{
  "event_count": 217,
  "first_events": [
    {
      "type": "answer_delta",
      "content": "直接"
    },
    {
      "type": "answer_delta",
      "content": "回答"
    },
    {
      "type": "answer_delta",
      "content": "：\n"
    }
  ],
  "final_events": [
    {
      "type": "sources",
      "sources_count": 7
    },
    {
      "type": "trace",
      "trace_steps": [
        "query_analysis",
        "retrieval_planning",
        "retrieval",
        "generate_answer"
      ]
    },
    {
      "type": "done"
    }
  ],
  "answer_delta_preview": "直接回答：\nQdrant 是一个面向 AI 应用的向量相似性搜索引擎和向量数据库，用于存储、搜索和管理带有附加载荷的向量数据，支持语义搜索、混合搜索、相似性匹配、推荐系统以及从非结构化数据中提取信息...",
  "source_count": 7
}
```

## 5. Run Agent

Command:

```bash
curl -sS -X POST http://127.0.0.1:8010/agent/run \
  -H "Content-Type: application/json" \
  -d '{"question":"What is Qdrant used for in vector search?"}'
```

Observed response excerpt:

```json
{
  "answer": "直接回答：\nQdrant 是一个向量相似性搜索引擎和向量数据库，用于存储、搜索和管理带有附加载荷的向量数据。它主要用于基于神经网络或语义的匹配、分面搜索、推荐系统，以及从非结构化数据中提取有意义的信息...",
  "source_count": 7,
  "selected_tool": "retrieval_tool",
  "tool_status": "success",
  "tool_output_keys": [
    "answer",
    "sources",
    "trace"
  ],
  "trace": [
    {
      "step": "analyze_question",
      "status": "completed",
      "detail": {
        "needs_retrieval": true,
        "question_type": "general",
        "reason": "normal knowledge question, use retrieval"
      }
    },
    {
      "step": "plan_tool",
      "status": "completed",
      "detail": {
        "tool_name": "retrieval_tool",
        "reason": "question requires knowledge retrieval"
      }
    },
    {
      "step": "execute_tool",
      "status": "success",
      "detail": {
        "tool_name": "retrieval_tool",
        "attempts": [
          {
            "attempt": 1,
            "status": "success"
          }
        ]
      }
    }
  ]
}
```

## Current Evidence

This demo verifies the current end-to-end path:

```text
upload -> ingest -> retrieve -> generate answer -> return sources -> stream answer -> agent tool execution
```

The strongest evidence from this run:

- Upload and ingest accept a Markdown file and store one chunk.
- `/ask` returns a grounded answer, source references, and RAG trace.
- `/ask/stream` returns NDJSON answer deltas, sources, trace, and `done`.
- `/agent/run` selects `retrieval_tool`, executes it successfully, and returns Agent trace.

## Known Limits

- The Agent planner is still rule based. This run does not demonstrate native
  function calling or model-selected tool calls.
- The response latency is not optimized. In this run, non-streaming answer
  generation took about 31 seconds.
- Streaming retrieval currently relies on the streaming path implementation.
  The roadmap still calls out retry consistency between streaming and
  non-streaming RAG paths as a follow-up.
- This is a local demo against one representative question, not a broad quality
  or latency benchmark.
