# AGENT

这是一个从 RAG 知识库问答逐步演进到轻量 Agent 编排的 AI 应用工程项目。

当前仓库结构把 RAG 作为 Agent 系统的第一个可运行子项目。后续 Agent 编排层会在此基础上增加问题分析、检索路由、执行 trace 和回答组织能力。

## 子项目

| 子项目 | 状态 | 说明 |
| --- | --- | --- |
| `rag` | 已完成 MVP | 支持 Markdown/PDF 入库、Qdrant 检索、FastAPI 问答、来源引用和离线评测 |

## 当前运行方式

进入 RAG 子项目：

```bash
cd rag
```

然后按照 [`rag/README.md`](rag/README.md) 运行。

## English

This repository is evolving from a RAG knowledge-base application into a lightweight Agent project. The current runnable module is [`rag`](rag/), which provides document ingestion, Qdrant retrieval, FastAPI question answering, cited sources, and evaluation scripts.
