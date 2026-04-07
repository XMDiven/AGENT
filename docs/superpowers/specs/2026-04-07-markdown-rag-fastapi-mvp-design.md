# Markdown RAG FastAPI MVP 设计文档

## 1. 目标

本阶段要实现一个最小可用的 Markdown RAG 系统。

系统先离线读取本地 Markdown 文档并写入向量库，再通过 FastAPI 暴露 `POST /ask` 接口，为用户返回基于检索上下文生成的答案。

第一版的核心目标不是功能齐全，而是把下面这条主链路稳定跑通：

```text
Markdown 文件 -> 切块 -> 向量化 -> 写入 Qdrant -> 检索 -> 生成答案 -> 返回 answer + sources
```

## 2. MVP 边界

### 2.1 本阶段包含的能力

- 只处理 `data/raw/` 目录下的 Markdown 文件
- 通过脚本构建索引，不提供 ingestion HTTP 接口
- 对外只暴露一个 `POST /ask` 接口
- 请求体只包含 `question`
- 响应体包含 `answer` 和 `sources`
- `sources` 中只返回 `source`、`section_path`、`snippet`
- 如果检索不到足够上下文，返回保守的 fallback answer

### 2.2 本阶段明确不做的能力

- 文件上传
- `/ingest` 或 `/reindex` HTTP 接口
- rerank
- query rewrite
- 多轮对话记忆
- 多检索器组合
- 增量索引与重复写入保护
- 复杂 citation 格式

## 3. 验收标准

第一版完成后，应满足下面 5 条验收标准：

1. 运行建索引脚本后，Qdrant 中能够查到 Markdown 切块
2. 启动 FastAPI 后，`POST /ask` 能返回非空 JSON
3. 响应 JSON 中至少包含 `answer` 和 `sources`
4. `sources` 能反映答案来自哪个 Markdown 文件和哪个标题路径
5. 当问题超出文档范围时，接口返回 fallback answer，而不是编造答案

## 4. 架构设计

### 4.1 总体架构

系统拆为四层：

- `ingestion`
  负责加载 Markdown、切块、补 metadata
- `infrastructure`
  负责 embedding、LLM、Qdrant 的底层接入
- `retrieval` 与 `generation`
  负责检索策略和答案生成
- `services` 与 `app`
  负责应用编排和 FastAPI 对外暴露

这样的拆分可以让 HTTP、业务流程、向量库、Prompt 彼此独立，便于学习和调试。

### 4.2 数据流

#### 建索引链路

```text
build_index.py
-> 扫描 data/raw/*.md
-> ingest_service.py
-> markdown_loader.py
-> markdown_chunker.py
-> vectore_store.py
```

#### 问答链路

```text
POST /ask
-> app/routers/ask.py
-> services/ask_service.py
-> retrieval/retriever.py
-> generation/context_formatter.py
-> generation/qa_prompt.py
-> generation/answer_generator.py
-> 返回 answer + sources
```

## 5. 模块职责

### 5.1 建索引相关

#### `src/scripts/build_index.py`

职责：

- 作为建索引脚本入口
- 扫描 `data/raw/` 下的 Markdown 文件
- 调用 ingest service 处理每个文件
- 输出处理文件数和 chunk 数

限制：

- 不直接操作 Qdrant SDK
- 不包含 HTTP 逻辑

#### `src/services/ingest_service.py`

职责：

- 负责编排 `load_markdown -> chunk_markdown -> ingest_chunks`
- 返回单文件处理结果，例如 chunk 数和写入条数

限制：

- 不处理 FastAPI 请求
- 不拼接 Prompt

#### `src/ingestion/loaders/markdown_loader.py`

职责：

- 将单个 Markdown 文件转换为 `Document` 列表

限制：

- 只负责读取，不负责切块和向量化

#### `src/ingestion/chunkers/markdown_chunker.py`

职责：

- 按 Markdown 标题切分
- 按字符长度进一步切分
- 为每个 chunk 补齐 metadata

期望 metadata 至少包括：

- `source`
- `doc_type`
- `section_path`

#### `src/infrastructure/vectore_store.py`

职责：

- 返回 `QdrantVectorStore`
- 将切块写入 Qdrant

限制：

- 不包含问答业务逻辑

### 5.2 问答相关

#### `src/retrieval/retriever.py`

职责：

- 通过 `vector_store.as_retriever(...)` 返回 retriever
- 集中配置 `search_type` 与 `top_k`

限制：

- 不直接生成答案

#### `src/services/ask_service.py`

职责：

- 编排完整问答链路
- 完成检索、空结果处理、context 格式化、生成答案、组装 sources

推荐主流程：

```text
get_retriever()
-> retriever.invoke(question)
-> 空结果时直接返回 fallback
-> format_context(documents)
-> generate_answer(...)
-> assemble_sources(documents)
```

#### `src/generation/context_formatter.py`

职责：

- 将检索到的 `Document` 列表格式化为提供给 LLM 的上下文字符串

要求：

- 每个 block 应该有稳定编号
- 便于模型引用

#### `src/generation/qa_prompt.py`

职责：

- 提供唯一的 QA Prompt 模板

要求：

- 明确要求模型只基于上下文回答
- 明确要求中文输出
- 明确在上下文不足时承认不知道

#### `src/generation/answer_generator.py`

职责：

- 执行 `prompt | llm | StrOutputParser()` 这条生成链

限制：

- 不直接关心 FastAPI、retriever、Qdrant

### 5.3 API 层

#### `src/schemas/ask_schema.py`

职责：

- 定义 `AskRequest`
- 第一版只包含 `question: str`

#### `src/schemas/answer_schema.py`

职责：

- 定义 `SourceItem`
- 定义 `AnswerResponse`

建议结构：

```json
{
  "answer": "string",
  "sources": [
    {
      "source": "string",
      "section_path": "string",
      "snippet": "string"
    }
  ]
}
```

#### `app/routers/ask.py`

职责：

- 定义 `POST /ask`
- 接收请求
- 调用 `ask_service`
- 返回 `AnswerResponse`

限制：

- 不写具体 RAG 业务逻辑

#### `app/main.py`

职责：

- 创建 FastAPI app
- 注册 `ask` 和 `health` 路由

## 6. 错误处理

第一版只处理下面 4 类错误：

### 6.1 请求不合法

- 交给 FastAPI 与 Pydantic 自动返回 422

### 6.2 检索结果为空

- 不调用 LLM
- 直接返回：
  - `answer = config.FALLBACK_ANSWER`
  - `sources = []`

### 6.3 基础设施配置缺失

例如：

- `QDRANT_URL`
- `QDRANT_COLLECTION`
- `EMBEDDING_BASE_URL`
- `EMBEDDING_MODEL`
- `BASE_URL`
- `LLM_MODEL_ID`

处理策略：

- 尽早抛错
- 不静默吞掉异常

### 6.4 模型或向量库调用失败

处理策略：

- 由 service 向上抛出异常
- 路由层返回 500
- 日志中保留原始异常信息

第一版不做复杂重试。

## 7. 响应格式设计

### 7.1 请求体

```json
{
  "question": "LangChain 是什么？"
}
```

### 7.2 成功响应

```json
{
  "answer": "LangChain 是一个用于构建 LLM 应用的框架。",
  "sources": [
    {
      "source": "data/raw/langchain.md",
      "section_path": "Introduction > Overview",
      "snippet": "LangChain is a framework for developing applications powered by language models."
    }
  ]
}
```

### 7.3 空检索响应

```json
{
  "answer": "我无法仅根据当前检索到的上下文可靠回答这个问题。",
  "sources": []
}
```

## 8. 开发顺序

为了降低学习阶段的中断概率，推荐严格按下面顺序开发：

1. 先完成 `ingest_service.py`
2. 再完成 `build_index.py`
3. 然后定义 `ask_schema.py` 和 `answer_schema.py`
4. 再完成 `ask_service.py`
5. 然后补齐 `ask.py` 与 `app/main.py`
6. 最后补最小测试

推荐原因：

- 先让索引能跑起来，后面的 `/ask` 才有真实数据可以验证
- 先定接口契约，service 和 router 才不会反复改
- 主链路完成后再暴露 API，调试成本更低

## 9. 测试策略

第一版只要求最小 smoke test，不追求完整测试矩阵。

### 9.1 建索引 smoke test

运行建索引脚本，确认：

- 没有抛异常
- 输出了处理文件数或 chunk 数

### 9.2 问答 service smoke test

给一个文档内问题，确认：

- 返回非空 `answer`
- `sources` 非空

给一个文档外问题，确认：

- 返回 fallback answer
- `sources` 为空

### 9.3 API smoke test

调用 `POST /ask`，确认：

- 返回 200
- JSON 中有 `answer`
- JSON 中有 `sources`

## 10. 工程取舍

### 10.1 为什么不做 `/ingest` API

因为第一版的核心目标是掌握 RAG 主链路，而不是文件服务化。把 ingestion 放在脚本里，可以减少接口设计、幂等性、重复入库等问题对学习节奏的干扰。

### 10.2 为什么先不做 rerank 和 query rewrite

因为这些能力属于效果优化，不属于 MVP 闭环的必要条件。在基础链路未稳定前引入它们，只会增加排查复杂度。

### 10.3 为什么 `sources` 只返回 3 个字段

因为 `source`、`section_path`、`snippet` 已经足够支撑最小可解释性。第一版不需要把底层 metadata 全量暴露给调用方。

## 11. 风险与后续演进

### 11.1 当前风险

- 现有 `context_formatter.py` 的编号逻辑需要修正，否则 citation 不稳定
- 首次集合初始化流程需要确认是否与当前 Qdrant 用法兼容
- 当前仓库测试基础较薄，需要至少补一个 smoke test

### 11.2 后续自然演进方向

在 MVP 稳定后，可以按下面顺序继续增强：

1. 补 `/ingest` 或 `/reindex`
2. 增加 source 去重与排序优化
3. 增加 query rewrite
4. 增加 rerank
5. 支持更多文档类型，例如 PDF 或 OpenAPI
