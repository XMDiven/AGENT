# AGENT

这是一个从 RAG 知识库问答逐步演进到轻量 Agent 编排的 AI 应用工程项目。

当前仓库结构把 RAG 作为 Agent 系统的第一个可运行子项目。`rag` 子项目已经支持文档摄入、向量检索、问答生成、来源返回、轻量问题分析、检索规划、执行 trace、Prompt 版本管理和离线评测。`agent` 子项目在 RAG 之上提供轻量编排层，支持问题分析、工具规划、工具执行、Agent trace、工具失败状态返回和 FastAPI `/agent/run` 接口。

后续扩展方向是继续在 RAG 基线上演进更完整的 Agent 能力，例如工具调用、查询改写、多路检索和更复杂的执行规划。

## 子项目

| 子项目 | 状态 | 说明 |
| --- | --- | --- |
| `rag` | RAG MVP + 轻量编排基线 | 支持 Markdown/PDF 入库、Qdrant 检索、FastAPI 问答、来源引用、执行 trace、Prompt 版本和离线评测 |
| `agent` | 轻量 Agent 编排闭环 | 支持工具注册、问题分析、工具规划、工具执行、结构化 Agent trace、工具失败处理和 FastAPI `/agent/run` 接口 |

## 当前运行方式

进入 RAG 子项目：

```bash
cd rag
```

然后按照 [`rag/README.md`](rag/README.md) 运行。

进入 Agent 子项目：

```bash
cd agent
conda run -n AI_DEV pytest tests/ -q
```

Agent API 入口：

```bash
cd agent
conda run -n AI_DEV uvicorn agent_app.app.main:app --reload
```

更多说明见 [`agent/README.md`](agent/README.md)。

## English

This repository is evolving from a RAG knowledge-base application into a lightweight Agent project. The [`rag`](rag/) module provides document ingestion, Qdrant retrieval, FastAPI question answering, cited sources, lightweight query analysis, retrieval planning, execution traces, prompt versioning, and evaluation scripts. The [`agent`](agent/) module provides a lightweight orchestration layer with question analysis, tool planning, tool execution, Agent traces, structured tool failure handling, and a FastAPI `/agent/run` endpoint.
