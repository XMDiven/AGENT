# 给 Codex 的简历对齐与项目建设指南

> 本文件用于约束 Codex 在本仓库中如何一步一步指导用户，把项目推进到能够真实支撑简历项目经历的状态。
> 核心原则：先看代码和证据，再决定下一步；先补真实能力，再升级简历表述。

---

## 0. 当前扫描基线

最近一次扫描日期：2026-06-03。

本文件基于以下事实生成：

- 简历文件：`/Users/mdiven/Documents/Resume/Resume.docx`
- 当前仓库：`/Users/mdiven/Code/Projects/AGENT`
- 已扫描子项目：`rag`、`agent`
- 已扫描实验记录：`rag/experiments/`
- 已验证测试：
  - `cd rag && conda run -n AI_DEV pytest tests/ -q`：`87 passed`
  - `cd agent && conda run -n AI_DEV pytest tests/ -q`：`35 passed`

当前 git 工作区存在一个与本指南无直接关系的未跟踪文件：

- `agent_ai_app_interview_prep.html`

Codex 后续工作时不得把简历中的强表述直接当作项目事实。每次建议代码前，都应先回答：

1. 当前代码已经证明了什么？
2. 简历目标还缺什么证据？
3. 最小下一步是什么？
4. 做完后用什么测试、报告或演示验证？
5. 哪句简历可以升级，哪句仍然不能写？

---

## 1. 最终简历目标

用户目标岗位：**AI 应用开发实习**。

简历当前写了三段项目经历：

1. **基于 RAG 的智能知识库问答系统**
2. **LLM Agent 多工具编排系统**
3. **LLM Prompt 效果自动评测平台**

Codex 的默认任务不是一次性堆满所有功能，而是持续帮助用户把仓库推进到“面试时能讲清、代码里能指到、测试里能验证、报告里能量化”的状态。

---

## 2. 当前仓库事实

### 2.1 `rag` 子项目

当前定位：RAG 问答后端和 Prompt 评测基础。

当前较安全能力：

- FastAPI 应用入口：`rag/src/rag_app/app/main.py`
- 文档上传接口：
  - `POST /documents/upload`
  - `POST /documents/upload/batch`
- 单文件入库接口：
  - `POST /documents/ingest`
- 支持 Markdown / PDF 文件保存、解析、切分、向量化入库
- 上传文件只允许 `.md` 和 `.pdf`
- 上传和入库均做安全文件名处理，避免路径穿越
- Qdrant 向量库写入和检索
- `/ask` 非流式问答接口
- `/ask/stream` NDJSON 流式问答接口
- 返回 `answer`、`sources`、`trace`
- 轻量问题分析：`empty`、`general`、`comparison`、`summary`
- 检索规划：`skip_retrieval`、`standard_retrieval`、`comparison_retrieval`
- comparison 问题会交错多来源文档，提升多来源覆盖
- 向量检索失败时在 RAG 服务层进行有限重试：`MAX_RETRIEVAL_RETRY = 1`，即总计 2 次 retrieval attempt
- 回答生成失败时最多重试 1 次，即总计 2 次 generation attempt
- Prompt 版本：`qa_prompt_v1`、`qa_prompt_v2`
- 离线检索评估和回答评估
- LLM-as-Judge 结构化评分：
  - relevance
  - completeness
  - groundedness
  - format
- Prompt A/B 对比报告
- Prompt eval API：
  - `GET /prompt-evals/reports`
  - `GET /prompt-evals/reports/{run_id}`
  - `GET /prompt-evals/comparison/latest`
  - `POST /prompt-evals/run`
- `POST /prompt-evals/run` 支持通过 `prompt_version` 和可选 `case_limit` 同步触发小样本 LLM-as-Judge 评测并保存 report
- latency benchmark 脚本和报告
- 100 页 PDF 摄入验证报告

### 2.2 `agent` 子项目

当前定位：建立在 RAG 之上的轻量 Agent 编排层。

当前较安全能力：

- FastAPI 应用入口：`agent/src/agent_app/app/main.py`
- API：
  - `POST /agent/run`
  - `GET /health`
- Service 统一入口：`agent/src/agent_app/service.py`
- 工具规划：`agent/src/agent_app/orchestration/planner.py`
- 工具执行：`agent/src/agent_app/orchestration/executor.py`
- 状态对象：`agent/src/agent_app/orchestration/state.py`
- 工具注册表：`agent/src/agent_app/tools/registry.py`
- RAG 检索工具：`agent/src/agent_app/tools/retrieval.py`
- 本地确定性摘要工具：`agent/src/agent_app/tools/summary.py`
- 工具：
  - `retrieval_tool`
  - `summary_tool`
  - `question_decompose_tool`
  - `fallback_tool`
- 基于 `question_type` 的规则式工具选择
- `question_decompose_tool` 对比较类和多子问题输入做规则式拆解，并对子问题逐个调用 RAG 检索工具后聚合 `answer`、`sources`、`sub_results`
- Agent 层不再对 `retrieval_tool` 做 3 次整体 retry；向量检索 retry 下沉到 RAG 服务层
- 工具失败时返回结构化 `error_type`、`error`、`attempts`
- Agent trace 记录：
  - `analyze_question`
  - `plan_tool`
  - `execute_tool`

---

## 3. 简历强表述与当前证据边界

| 简历表述 | 当前判断 | Codex 后续处理 |
|---|---|---|
| PDF 批量上传 | 已支持基础上传 | 可写“支持 Markdown/PDF 单文件与批量上传”；不要把上传等同于自动入库 |
| 自动解析、向量化入库全流程 | 已有 `/documents/ingest` 和 `build_index` | 可写“上传后可触发单文件入库，或通过 build_index 批量重建索引” |
| 单文档 100+ 页稳定处理 | 有 100 页 PDF 报告，但仍是单样本离线验证 | 可写“验证 100 页级 PDF”；若简历坚持“100+ 页稳定”，建议补更严格样本和耗时记录 |
| 文档上传后自动入库 | 未自动触发 | 当前是上传与入库分离；不要写“上传后自动入库” |
| 流式返回 | 已支持 | 可写“支持 NDJSON 流式返回” |
| 平均响应时延 2s 内 | 明确不支持 | latency 报告显示平均约 24.43s；不能写 2s |
| 上下文命中率提升约 20% | 尚缺严格定义 | 有 Top-K 从 10/11 到 11/11 的对比；不能直接写 20% |
| Fixed-size / Semantic / Recursive 三种 Chunk 策略 | 当前不完整 | 代码主要是 Markdown header + RecursiveCharacterTextSplitter；Semantic 未实现 |
| ChromaDB / FAISS | 与当前主线不一致 | 当前主线是 Qdrant；若要写 Chroma/FAISS，必须真实实现 |
| AutoGen | 未实现 | 不应写；更安全写“自建轻量 Agent 编排层” |
| Function Calling | 未实现 | 不应写；可后续新增工具 schema 和受控 tool calling |
| 网络搜索工具 | 未实现 | 不应写，除非真实接入或明确 mock 边界 |
| 信息摘要工具 | 基础支持 | 当前是本地确定性摘要，不是 LLM 摘要 |
| 任务拆解工具 | 已实现最小规则式版本 | 可写“规则式问题拆解工具”；不要写成 LLM 自主规划 |
| 复杂用户意图自动规划 | 未实现 | 当前是规则式 planner；不要包装成自主规划 |
| 检索失败自动重试 | 已在 RAG 服务层支持向量检索有限重试 | 可写“对向量检索失败进行有限重试并写入 trace”；不要写成所有工具统一 3 次 retry |
| 结构化日志 | 部分支持 | 当前是结构化 trace，不是完整日志系统 |
| Prompt 自动评测平台 | 部分支持 | 有离线评测、LLM-as-Judge、报告读取 API；还不是可配置运行平台 |
| KIMI Judge | 环境可用 OpenAI-compatible/Moonshot | 可写“接入 OpenAI-compatible/Kimi 类 Judge 模型”，但要以实际 `.env` 和报告为准 |
| A/B Prompt 对比 | 已有 11 case 对比报告 | 可写“小样本 Prompt A/B 对比”；不能写 80+ 组 |
| 80+ 组 Prompt 对比、300+ 样本 | 未支持 | 必须真实扩样本和记录运行 |
| 单次评测耗时 2.8s | 未支持 | 当前 judge 报告耗时远高于 2.8s；不能写 |
| 30 分钟压缩到 10 分钟 | 未支持 | 需要人工 baseline 和自动流程对比 |

---

## 4. Codex 默认指导格式

用户每次提出新需求时，Codex 应优先用下面格式回答，除非用户明确说“直接实现”。

1. **结论**：这一步是否值得做
2. **简历对齐**：支撑简历中的哪句话
3. **当前状态**：仓库已有哪个基础
4. **最小缺口**：还差什么
5. **建议任务**：这一步只做什么
6. **不做什么**：明确排除范围，避免过度设计
7. **验收方式**：测试、命令、报告或 API 演示
8. **简历影响**：完成后哪句更安全，哪句仍不能写

如果用户问“下一步做什么”，Codex 应从当前代码状态出发，推荐最小、可验证、最直接支撑简历的任务。

如果用户要求写代码，Codex 应先定义成功标准，再做小步改动，并在完成后运行对应测试。

---

## 5. 总体建设顺序

Codex 应按下面顺序指导用户推进，不要跳阶段：

1. **阶段 0：证据基线整理**
2. **阶段 1：RAG 简历目标补齐**
3. **阶段 2：Agent 编排目标补齐**
4. **阶段 3：Prompt 评测平台目标补齐**
5. **阶段 4：最终简历措辞回收与降级检查**

优先级原则：

- 先做最接近当前仓库的能力
- 先做能测试、能演示、能写报告的能力
- 不为简历堆无用框架
- 不为了匹配词汇强行引入 AutoGen、FAISS 或复杂前端
- 每次实现后必须回到简历表述，判断能否升级

---

## 6. 阶段 0：证据基线整理

### 目标

先把当前已经完成的能力固定成证据，避免后续 Codex 反复猜测项目状态。

### Codex 应指导用户完成

1. 运行 RAG 测试：

   ```bash
   cd rag
   conda run -n AI_DEV pytest tests/ -q
   ```

2. 运行 Agent 测试：

   ```bash
   cd agent
   conda run -n AI_DEV pytest tests/ -q
   ```

3. 如需要更新评估基线，再运行 RAG eval：

   ```bash
   cd rag
   docker compose up -d qdrant
   conda run -n AI_DEV python -m rag_app.scripts.reset_index
   conda run -n AI_DEV python -m rag_app.scripts.build_index
   conda run -n AI_DEV python -m rag_app.scripts.run_eval
   ```

4. 保存或确认以下证据：

   - RAG 测试通过数量
   - Agent 测试通过数量
   - 最新 `experiments/evaluation_runs/*.json`
   - 最新 `experiments/judge_runs/*.json`
   - `/ask` 示例响应
   - `/ask/stream` 示例输出
   - `/documents/upload` 示例响应
   - `/documents/ingest` 示例响应
   - `/agent/run` 示例响应

### 完成后安全简历说法

```text
基于 FastAPI 实现 RAG 问答后端，支持文档摄入、语义检索、来源引用返回，并通过离线评估脚本验证检索与回答质量。
```

### 仍不能写

- 2s 延迟
- 80+ Prompt 对比
- 300+ 样本
- AutoGen
- Function Calling
- 外部网络搜索工具
- 复杂自主规划

---

## 7. 阶段 1：RAG 简历目标补齐

### 目标

让 `rag` 子项目尽量接近最终简历第一段：

```text
PDF 批量上传 -> 自动解析 -> 向量化入库 -> 语义检索 -> 问答接口 -> 流式返回 -> 来源引用 -> 检索调优证据
```

### 1.1 文档上传与入库链路

当前状态：

- 已有 `/documents/upload`
- 已有 `/documents/upload/batch`
- 已有 `/documents/ingest`
- 上传接口只保存到 `data/raw/`
- `/documents/ingest` 对单个已上传文件执行解析、切分、向量化入库
- 批量重建索引仍通过 `build_index`

Codex 下一步应指导：

1. 不要把上传接口直接说成自动入库。
2. 先把“上传”和“入库”两个步骤讲清楚。
3. 若用户想更贴近简历，可新增最小的 batch ingest 能力，而不是把复杂逻辑塞进 upload router。

验收证据：

- `rag/tests/api/test_documents_api.py`
- README 中 `/documents/upload`、`/documents/upload/batch`、`/documents/ingest` 示例
- 手动演示一次：上传文件 -> 调用 `/documents/ingest` -> 返回 `document_count`、`chunk_count`、`stored_count`

安全简历说法：

```text
支持 Markdown/PDF 单文件与批量上传，并提供单文件入库接口完成解析、切分和向量化写入。
```

只有实现并验证后才能写：

```text
支持上传后自动入库。
```

### 1.2 100 页级 PDF 处理

当前状态：

- 已有报告：`rag/experiments/large_pdf_ingestion_report.md`
- 报告验证了 `gpt4_technical_report.pdf` 共 100 页
- 历史入库记录：`documents=100`、`chunks=452`、`stored=452`
- 当前 Qdrant count 验证为 452
- 评估 case 命中该 PDF 来源

Codex 下一步应指导：

1. 如果用户只需要面试可讲，先保留现有报告。
2. 如果简历坚持“100+ 页稳定处理”，建议补一次更严格验证：
   - 使用大于 100 页的 PDF
   - 重新运行完整 build_index 或单文件 ingest
   - 记录耗时、chunk 数、stored 数、失败情况
3. 不要把单样本离线验证包装成生产级稳定性。

验收证据：

- `rag/experiments/large_pdf_ingestion_report.md`
- 对应 eval report
- 必要时新增更新后的大文档报告

安全简历说法：

```text
验证 100 页级 PDF 的解析、切分、向量化入库和检索命中流程，并记录 documents/chunks/stored 等处理结果。
```

谨慎写法：

```text
在本地实验环境验证单文档 100 页级 PDF 的知识库构建流程。
```

### 1.3 问答接口、来源引用与 trace

当前状态：

- 已有 `/ask`
- 返回 `answer`
- 返回结构化 `sources`
- 返回 RAG trace
- trace 包含 query analysis、retrieval planning、retrieval、generation
- answer eval 检查来源、fallback、元数据泄漏和 v2 输出结构

Codex 下一步应指导：

1. 保持响应结构稳定。
2. 补充 1 到 2 个面试演示问题。
3. 如果改动 prompt 或 sources 契约，必须重新跑对应测试。

验收证据：

- `rag/tests/api/test_ask_api.py`
- `rag/tests/services/test_ask_service.py`
- `rag/experiments/evaluation_runs/*.json`

安全简历说法：

```text
封装问答接口，返回带来源引用的 grounded answer，并通过回答评估检查来源契约。
```

### 1.4 流式返回

当前状态：

- 已有 `/ask/stream`
- 使用 `application/x-ndjson`
- 返回事件：
  - `answer_delta`
  - `sources`
  - `trace`
  - `done`

Codex 下一步应指导：

1. 不重复实现 streaming endpoint。
2. 保留手动演示记录。
3. 如果继续优化，再拆分首 token 延迟和完整回答耗时。

验收证据：

- `rag/tests/api/test_ask_api.py`
- README curl 示例
- 手动 `curl -N` 输出

安全简历说法：

```text
支持基于 NDJSON 事件的流式问答返回。
```

### 1.5 延迟 benchmark

当前状态：

- 已有脚本：`rag/src/rag_app/scripts/benchmark_latency.py`
- 已有报告：`rag/experiments/latency_benchmark.md`
- 当前有效基线平均耗时约 `24.43s`
- 主要瓶颈是 LLM 生成阶段，不是 Qdrant 检索阶段
- 当前不能支撑“2s 内”

Codex 下一步应指导：

1. 不要为了简历硬写 2s。
2. 若要优化延迟，优先验证生成侧变量：
   - 更快模型
   - 更短 prompt
   - 更短回答长度
   - 更小上下文 token budget
3. 每次优化都必须更新 benchmark 报告，而不是只看一次手动调用。

验收证据：

- `rag/experiments/latency_benchmark.md`
- benchmark 命令输出
- 平均值、最大值、最小值、case 明细

当前安全简历说法：

```text
设计 RAG latency benchmark，对完整问答链路进行分段耗时统计，并定位主要瓶颈来自 LLM 生成阶段。
```

当前不能写：

```text
平均响应时延控制在 2s 以内。
```

### 1.6 检索调优与命中率提升

当前状态：

- 已有报告：`rag/experiments/retrieval_chunk_experiment.md`
- chunk size 对比覆盖 200/400/800
- Top-K 对比中，从 `top_k=2` 的 `10/11` 到 `top_k=5/7` 的 `11/11`
- 当前默认 `RETRIEVAL_TOP_K = 7`
- 尚未严格定义“上下文命中率”
- 尚不能写“提升约 20%”

Codex 下一步应指导：

1. 先定义指标，例如 source hit rate、all-source hit rate 或 answer pass rate。
2. 固定 baseline、case set、配置。
3. 明确计算公式。
4. 如果样本只有 11 个，要在报告中说明样本量限制。
5. 不要把 10/11 到 11/11 强行写成 20%。

验收证据：

- `rag/experiments/retrieval_chunk_experiment.md`
- `rag/experiments/retrieval_eval_cases.json`
- 新增或更新的评估报告

安全简历说法：

```text
对比 chunk size 和 Top-K 配置，并基于离线评估结果选择当前检索基线。
```

只有数据支持后才能写：

```text
上下文命中率提升约 20%。
```

### 1.7 Chunk 策略边界

当前状态：

- Markdown 使用 Markdown header splitting + RecursiveCharacterTextSplitter
- PDF 使用 RecursiveCharacterTextSplitter
- 有 chunk size 参数实验
- 未发现独立 Semantic chunker
- 未发现完整 Fixed-size / Semantic / Recursive 三策略对比实现

Codex 下一步应指导：

1. 不要直接写“三种 Chunk 策略”。
2. 如果要补简历强表述，优先新增可测试的 chunking strategy 抽象和最小实验。
3. 如果不补代码，就把简历降级为“对 chunk size 和 Top-K 做实验”。

安全简历说法：

```text
基于 Markdown 标题结构和 RecursiveCharacterTextSplitter 构建切分流程，并对 chunk size 与 Top-K 参数进行离线评估。
```

---

## 8. 阶段 2：Agent 编排目标补齐

### 目标

让 `agent` 子项目逐步接近最终简历第二段：

```text
问题分析 -> 工具规划 -> 工具注册 -> 工具执行 -> 状态管理 -> trace -> 失败处理 -> 可扩展工具链
```

当前不要把它包装成 AutoGen、多 Agent 或复杂自主规划系统。

### 2.1 固定当前 Agent 基线

当前状态：

- 已有 `retrieval_tool`
- 已有 `summary_tool`
- 已有 `fallback_tool`
- 已有工具注册表
- 已有规则式 planner
- 已有 executor
- 已有 `AgentState`
- 已有 `/agent/run`
- 已有结构化 trace
- 已有 `question_decompose_tool`，用于比较类和多子问题的规则式拆解
- 拆解后的子问题会逐个调用 RAG 检索工具，并聚合 `answer`、`sources`、`sub_results`
- Agent 层负责工具编排、状态记录和结果聚合；检索 retry 由 RAG 服务层处理
- 当前测试基线：`35 passed`

Codex 下一步应指导用户确认：

1. Agent 测试通过。
2. `/agent/run` 空问题走 fallback。
3. 普通知识问题走 retrieval。
4. 总结类问题走 summary。
5. retrieval 工具失败时返回 failed 和 attempts；RAG 检索失败重试由 RAG trace 记录。

验收证据：

- `agent/tests/`
- `agent/README.md`
- `/agent/run` 示例响应

安全简历说法：

```text
在 RAG 系统之上实现轻量 Agent 编排层，支持问题分析、工具选择、工具执行和结构化 trace 返回。
```

### 2.2 工具注册层

当前状态：

- `ToolDefinition` 当前只有 `name` 和 `description`
- 工具注册表位于 `agent/src/agent_app/tools/registry.py`

Codex 下一步应指导：

1. 先保持工具定义简单。
2. 若要支撑更强简历，可逐步补：
   - input schema
   - output schema
   - error schema
   - retry policy
3. 不要一开始设计复杂插件系统。

验收证据：

- `agent/src/agent_app/tools/registry.py`
- `agent/tests/test_tools.py`
- 未知工具错误测试

安全简历说法：

```text
将工具注册和执行逻辑拆分，降低新增工具的接入成本。
```

### 2.3 新增真实工具

当前状态：

- `retrieval_tool` 已存在
- `summary_tool` 已存在，但只是本地确定性摘要
- `fallback_tool` 已存在
- 网络搜索工具未实现
- 已实现 `question_decompose_tool`，用于规则式拆解比较类和多子问题输入

推荐新增顺序：

1. 更真实的 `summary_tool`，例如对长文本或检索结果做摘要
2. 扩展工具 schema，为后续受控 tool calling 做准备
3. 受控的 `web_search_tool`，只有在 API、mock 边界和失败处理明确后再做

Codex 应优先建议本地可控工具，不要一开始接外部搜索。

验收证据：

- 每个工具有单元测试
- 每个工具有成功输出
- 每个工具有失败输出
- `/agent/run` trace 能看到工具名和状态

安全简历说法：

```text
集成检索、摘要和兜底工具，支持基于问题类型的工具选择与执行。
```

当前已可升级为：

```text
集成检索、摘要和问题拆解等工具，支持基于问题类型的工具选择、子问题检索聚合与执行 trace 返回。
```

只有真实接入后才能写：

```text
集成网络搜索工具。
```

### 2.4 Planner 从规则升级到更强策略

当前状态：

- 当前 planner 是规则式
- 根据 RAG `query_analyzer` 的 `question_type` 选择工具
- 已通过规则信号选择 `question_decompose_tool`
- 不调用 LLM planner
- 不使用 Function Calling

Codex 下一步应指导：

1. 维护当前规则式 planner 边界，不要包装成 LLM 自主规划。
2. README 和简历只写“规则式问题拆解”和“结构化 trace”。
3. 当工具数量和输入输出 schema 更稳定后，再考虑 Function Calling。
4. 不建议为了简历词汇直接引入 AutoGen。

验收证据：

- planner 单元测试覆盖不同 `question_type`
- trace 中记录 planner reason
- README 解释 planner 边界

安全简历说法：

```text
设计问题分析与工具规划模块，根据问题类型选择合适工具并返回可追踪执行过程。
```

### 2.5 状态管理与 trace

当前状态：

- 已有 `AgentState`
- 已有 trace
- API 返回 `answer`、`sources`、`selected_tool`、`tool_status`、`tool_output`、`trace`

Codex 下一步应指导：

1. 保持 state 字段清晰。
2. trace 每步包含 `step`、`status`、`detail`。
3. 工具失败也必须进入 trace。
4. 不要把 trace 写成不可读的大对象。

验收证据：

- `agent/tests/test_service.py`
- `agent/tests/api/test_run_api.py`
- README 示例

安全简历说法：

```text
使用结构化状态对象保存问题分析、工具计划、工具结果和执行轨迹。
```

### 2.6 失败重试与鲁棒性

当前状态：

- RAG 服务层对向量检索失败进行有限重试：`MAX_RETRIEVAL_RETRY = 1`，即总计 2 次 retrieval attempt
- RAG generation 是 `MAX_GENERATION_RETRY = 1`，即总计 2 次 generation attempt
- Agent 层不再对 `retrieval_tool` 做 3 次整体 retry，避免多子问题场景放大下游调用次数
- FastAPI/Pydantic 提供基础请求校验
- 当前是结构化 trace，不是完整日志系统

Codex 下一步应指导：

1. 不要笼统说“所有工具都重试 3 次”。
2. retry 应尽量靠近真实失败点：向量库失败在 RAG 检索层处理，LLM 生成失败在 generation 层处理。
3. Agent 层只记录工具调用状态、子问题聚合结果和 trace，不做粗粒度整体 retry。
4. 如果新增外部工具，再按工具风险设计单独 retry policy。
5. 若要写“结构化日志”，建议新增真正 logging 层；否则写“结构化 trace”。

验收证据：

- `agent/tests/test_executor.py`
- `rag/tests/services/test_ask_service.py`
- failed trace 示例
- README 说明重试边界

安全简历说法：

```text
在 RAG 服务层对向量检索和回答生成失败进行有限重试，并通过结构化 trace 暴露 retrieval/generation 的状态与耗时。
```

### 2.7 AutoGen 与 Function Calling 边界

当前状态：

- 未发现 AutoGen
- 未发现真实 Function Calling

Codex 必须提醒用户：

1. 不要为了简历词汇硬引入 AutoGen。
2. 如果最终简历必须写 AutoGen，需要真实使用并能解释为什么需要。
3. 如果最终简历必须写 Function Calling，需要真实工具 schema、模型 tool call、调用链路和测试。
4. 更推荐当前阶段写“工具注册与结构化工具调用编排”。

安全替代表述：

```text
基于工具注册表和结构化 trace 实现轻量工具调用编排。
```

---

## 9. 阶段 3：Prompt 评测平台目标补齐

### 目标

让 Prompt 评测从当前离线 eval 和只读报告 API，逐步升级到能支撑最终简历第三段的能力：

```text
多版本 Prompt -> 固定测试样本 -> LLM-as-Judge -> Pydantic 评分 schema -> A/B 对比 -> 历史结果追溯 -> 可配置 API 演示
```

### 3.1 固定当前 eval 基线

当前状态：

- 有 retrieval eval
- 有 answer eval
- 有 `qa_prompt_v1` 和 `qa_prompt_v2`
- 有 JSON report
- 有 LLM-as-Judge report
- 有 Prompt A/B 对比报告
- golden set 当前为 11 个 case

Codex 下一步应指导：

1. 确认 eval cases 是否稳定。
2. 确认 report 中包含 prompt_version。
3. 确认 failed_cases 是否可读。
4. 不要口头比较 Prompt，必须保存报告。

安全简历说法：

```text
设计离线评估流程，对检索命中、回答来源契约和 Prompt 版本进行回归检查，并将结果保存为结构化报告。
```

### 3.2 Prompt 版本管理

当前状态：

- `qa_prompt_v1` 和 `qa_prompt_v2` 已存在
- `QA_PROMPT_VERSION` 可通过环境变量切换
- `run_eval` 会记录 `prompt_version`
- `qa_prompt_v2` 要求固定结构：
  - `Direct answer:`
  - `Key evidence:`
  - `Limitations:`

Codex 下一步应指导：

1. 明确 v1 和 v2 的差异。
2. 每次 prompt 改动必须升级版本或记录原因。
3. eval report 必须保存 prompt_version。
4. 默认 prompt 的选择要基于报告，不基于主观感觉。

验收证据：

- `rag/src/rag_app/generation/qa_prompt.py`
- `rag/tests/generation/test_qa_prompt.py`
- report 中有 `prompt_version`
- README 有按版本运行命令

安全简历说法：

```text
支持多版本 Prompt 配置，并通过统一评估脚本对比不同版本输出。
```

### 3.3 LLM-as-Judge

当前状态：

- 已支持最小 LLM-as-Judge 闭环：
  - `ask_question`
  - `answer/sources`
  - judge prompt
  - Pydantic schema
  - JSON report
- 已有代表性报告：`rag/experiments/llm_judge_report.md`
- 已有 judge runs：
  - `rag/experiments/judge_runs/20260526-162728.json`
  - `rag/experiments/judge_runs/20260526-211450.json`
  - `rag/experiments/judge_runs/20260526-212913.json`

Codex 下一步应指导：

1. 不重复新增 judge 基础链路。
2. 优先提高可复用性和可配置性。
3. 如果要写平台，下一步是 API 触发运行和配置 case set。
4. 如果要写 KIMI，必须确认实际环境变量和模型配置。

验收证据：

- `rag/src/rag_app/evaluation/judge_schema.py`
- `rag/src/rag_app/evaluation/answer_judge.py`
- `rag/src/rag_app/scripts/evaluate_answers_with_judge.py`
- `rag/tests/evaluation/test_answer_judge.py`
- `rag/tests/scripts/test_evaluate_answers_with_judge.py`
- `rag/experiments/llm_judge_report.md`

安全简历说法：

```text
实现基于 LLM-as-Judge 的评分链路，使用 Pydantic 定义相关性、完整性、事实支撑性和格式规范性评分结果。
```

### 3.4 A/B Prompt 对比

当前状态：

- 已有 `qa_prompt_v1` 和 `qa_prompt_v2`
- 已有 11 case 的 A/B 报告
- 报告路径：`rag/experiments/prompt_comparison_report.md`
- 报告记录分项分数、通过数、耗时和默认 Prompt 决策
- 当前不是 80+ 组，也不是 300+ 样本

Codex 下一步应指导：

1. 将当前报告作为 baseline。
2. 后续 Prompt 改动必须生成新的 judge report。
3. 不要口头比较 Prompt。
4. 若要升级平台，再补 API、case set 配置和历史查询。

验收证据：

- `rag/experiments/prompt_comparison_report.md`
- 对应 judge run JSON
- `GET /prompt-evals/comparison/latest`

安全简历说法：

```text
基于固定 golden questions 对 Prompt 版本进行结构化横向对比，并保存历史评测结果。
```

### 3.5 Prompt eval API

当前状态：

- 已有 Prompt Eval API：
  - `GET /prompt-evals/reports`
  - `GET /prompt-evals/reports/{run_id}`
  - `GET /prompt-evals/comparison/latest`
  - `POST /prompt-evals/run`
- API 可以读取历史 judge report 和 latest comparison
- `POST /prompt-evals/run` 已完成，支持通过 `prompt_version` 和可选 `case_limit` 同步触发小样本 LLM-as-Judge 评测，并将 report 写入 `experiments/judge_runs/`
- 尚未支持通过 API 传入任意 Prompt 模板、自定义测试用例或自定义评分维度

Codex 下一步应指导：

1. 不重复新增基础运行接口。
2. 如果用户要继续强化“平台化”，下一步优先补真实 API demo 证据，或支持自定义 case set。
3. 第三步再支持自定义评分维度。
4. 最后才考虑任意 Prompt 模板输入。

不建议一开始开放任意 Prompt 模板，原因是安全性、可复现性和报告对比都会变差。

验收证据：

- API schema
- API 测试
- README 示例
- eval report 落盘

完成最小运行接口后可写：

```text
封装 Prompt 评测 API，支持查询历史 LLM-as-Judge 报告、Prompt 对比指标，并按 Prompt 版本同步触发小样本评测运行与报告落盘。
```

只有真实支持后才能写：

```text
支持传入 Prompt 模板、测试用例与评分维度配置。
```

### 3.6 80+ 组实验、300+ 样本、耗时指标

当前状态：

- 当前 golden set 为 11 cases
- 当前 A/B 是 2 个 Prompt 版本
- 当前不支持 80+ 组或 300+ 样本
- 当前耗时也不能支撑 2.8s
- 当前没有人工 30 分钟 baseline 和自动 10 分钟对比证据

Codex 必须要求：

1. 真实生成或收集测试样本。
2. 明确样本来源。
3. 保存实验运行记录。
4. 统计实验数量。
5. 单独跑耗时 benchmark。
6. 如果使用外部 LLM，说明网络和模型波动限制。

没有这些证据，不允许写：

- `80+ 组 Prompt 对比实验`
- `300+ 条测试样本`
- `单次评测耗时 2.8s`
- `30 分钟压缩至 10 分钟`

安全替代表述：

```text
基于固定测试样本对 Prompt 版本进行结构化评估，并保存历史评测结果。
```

---

## 10. 阶段 4：最终简历表述升级规则

Codex 每次完成一个阶段后，都应帮助用户更新“可写 / 不可写”边界。

### 当前较安全版本

RAG：

```text
基于 FastAPI、LangChain 和 Qdrant 实现 RAG 问答后端，支持 Markdown/PDF 文档上传、单文件入库、语义检索、流式返回和来源引用，并通过离线评估脚本验证检索与回答质量。
```

Agent：

```text
在 RAG 系统之上实现轻量 Agent 编排层，支持问题分析、检索/摘要/问题拆解/兜底工具选择、子问题检索聚合、工具执行、状态管理和结构化 trace 返回。
```

Prompt eval：

```text
设计 Prompt 版本化评估流程，基于固定 golden questions 和 LLM-as-Judge 结构化评分，对不同 Prompt 版本的回答质量、groundedness 和耗时进行对比，并保存 JSON 评估报告。
```

### 当前可略强但仍真实的版本

RAG：

```text
验证 100 页级 PDF 的解析、切分、向量化入库和检索命中流程，并通过实验报告记录 documents/chunks/stored 等处理结果。
```

Prompt eval：

```text
封装 Prompt 评测 API，支持查看历史评测报告、最新 Prompt A/B 对比摘要，并按 prompt_version 触发小样本 Judge 评测运行。
```

### 仍需补证据后才能写的强版本

- 100+ 页多样本稳定处理
- 平均响应时延 2s 内
- 上下文命中率提升约 20%
- Semantic chunking 策略对比
- Function Calling
- AutoGen
- 网络搜索工具
- LLM-based 任务拆解工具
- 复杂用户意图自动规划
- 可传入 Prompt 模板、测试用例和评分维度的评测 API
- 80+ Prompt 对比实验
- 300+ 测试样本
- 单次评测 2.8s
- 人工 30 分钟压缩到自动 10 分钟

### 技术栈措辞规则

如果简历继续写 `ChromaDB / FAISS`，Codex 必须提醒：

- 当前代码主线是 Qdrant
- 写 Qdrant 最真实
- 若要写 ChromaDB / FAISS，必须真实补实现和测试

如果简历继续写 `AutoGen`，Codex 必须提醒：

- 当前 `agent` 是自建轻量编排层
- 写 AutoGen 不安全
- 更安全表述是“轻量 Agent 编排层”或“工具注册与执行框架”

如果简历继续写 `Function Calling`，Codex 必须提醒：

- 当前没有模型 tool call
- 当前只是本地规则式工具选择和工具执行
- 更安全表述是“工具注册表”和“结构化工具执行”

---

## 11. Codex 的默认下一步推荐

如果用户问“下一步做什么”，Codex 应默认推荐下面顺序。

| 优先级 | 任务 | 原因 | 验收 |
|---|---|---|---|
| P0 | 固定当前测试和 eval 基线 | 没有证据就无法安全写简历 | RAG 87 passed、Agent 35 passed、eval report |
| P1 | 更新 RAG README 中的演示链路 | 面试时最容易展示 | upload -> ingest -> ask -> stream |
| P1 | 把 100 页 PDF 报告补成可复现版本 | 支撑 RAG 第一段强表述 | 页数、chunks、stored、耗时 |
| P1 | 延迟优化前先保留 benchmark 结论 | 防止写错 2s 指标 | latency report |
| P2 | 已完成 `question_decompose_tool`，后续维护演示证据 | 直接支撑 Agent 第二段 | tool tests、planner tests、API trace、sub_results |
| P2 | 扩展工具 schema | 为 Function Calling 做准备但不提前承诺 | registry tests |
| P2 | 已完成 `POST /prompt-evals/run`，后续维护演示证据 | 支撑 Prompt 平台化 | API tests、report 落盘、README curl |
| P3 | 扩展 Prompt case set | 支撑更强样本规模 | case 来源、运行报告 |
| P3 | 再考虑 Function Calling 或 LangGraph | 只有工具链复杂后才有必要 | 设计说明、测试、README |

默认最小下一步建议：

```text
`question_decompose_tool`、RAG 检索层 retry 和 `POST /prompt-evals/run` 已完成。下一步优先补真实 API demo 证据和简历 bullet；若继续写功能，再考虑 Prompt eval 自定义 case set 或 Agent 工具 schema 扩展。
```

选择规则：

- 如果用户想强化第二段 Agent：先同步 README/简历表述，再考虑工具 schema 扩展
- 如果用户想强化第三段 Prompt 平台：先补 `POST /prompt-evals/run` 的 README/demo 证据，再考虑自定义 case set
- 如果用户想强化第一段 RAG：先更新大 PDF 和 latency 证据，不要再新增接口

---

## 12. 反过度设计规则

Codex 不应主动建议：

- 上来就换框架
- 为了 AutoGen 而 AutoGen
- 为了 FAISS 而重写向量层
- 为了平台感做复杂前端
- 没有数据就写提升百分比
- 没有 benchmark 就写延迟
- 明知 benchmark 不达标还写 2s
- 没有真实工具就写多工具 Agent
- 没有样本就写 300+ 测试
- 没有 API 触发运行就写完整 Prompt 平台

如果用户提出这些方向，Codex 应先问：

```text
这一步能直接支撑哪句简历？需要留下什么证据？有没有更小的实现方式？
```

---

## 13. 验收命令参考

RAG 测试：

```bash
cd rag
conda run -n AI_DEV pytest tests/ -q
```

RAG 评估：

```bash
cd rag
conda run -n AI_DEV python -m rag_app.scripts.run_eval
```

RAG Judge 评估：

```bash
cd rag
conda run --no-capture-output -n AI_DEV python -m rag_app.scripts.evaluate_answers_with_judge
```

RAG latency benchmark：

```bash
cd rag
conda run -n AI_DEV python -m rag_app.scripts.benchmark_latency
```

Agent 测试：

```bash
cd agent
conda run -n AI_DEV pytest tests/ -q
```

Agent CLI：

```bash
cd agent
conda run -n AI_DEV python -m agent_app.scripts.run_agent ""
```

RAG API 演示：

```bash
cd rag
conda run -n AI_DEV uvicorn rag_app.app.main:app --host 127.0.0.1 --port 8001 --reload
```

Agent API 演示：

```bash
cd agent
conda run -n AI_DEV uvicorn agent_app.app.main:app --host 127.0.0.1 --port 8000 --reload
```

每次完成任务后，Codex 应明确说明：

- 改了哪些文件
- 跑了什么命令
- 是否通过
- 生成了什么证据
- 简历哪句话更安全
- 哪句话仍然不能写

---

## 14. 最终原则

这个仓库不是为了堆概念，而是为了让用户在实习面试中能诚实讲清楚：

1. 系统怎么设计
2. 数据怎么流动
3. 为什么这样拆模块
4. 怎么验证效果
5. 指标从哪里来
6. 哪些能力是真做了
7. 哪些能力还只是下一阶段

当“简历更强”和“证据更真实”冲突时，Codex 必须优先选择证据真实。
