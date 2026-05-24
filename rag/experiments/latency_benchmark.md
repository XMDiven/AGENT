# RAG 问答延迟 Benchmark

## 测试环境

- 测试日期：2026-05-23
- 运行环境：本地开发环境
- 向量数据库：Qdrant
- 默认运行命令：`python -m rag_app.scripts.benchmark_latency`
- Top-K 对比命令：`RETRIEVAL_TOP_K=3 python -m rag_app.scripts.benchmark_latency`
- 测量范围：完整 `ask_question()` 在线问答链路

## 测试方法

本 benchmark 使用固定问题集调用 RAG 在线问答流程。

耗时统计包含：

- 问题分析
- 检索规划
- 向量检索
- 上下文格式化
- LLM 回答生成

其中 `retrieval_duration_seconds` 来自 `retrieval` trace，`generation_duration_seconds` 来自 `generate_answer` trace，`total_duration_seconds` 是 benchmark 脚本外层统计的完整调用耗时。

## 测试结果

### 有效模型基线：kimi-k2.5

本次有效 benchmark 使用 `kimi-k2.5`，所有 case 的 `generation_status` 均为 `completed`，`answer_is_fallback` 均为 `false`。

| case_id | total_duration_seconds | retrieval_duration_seconds | generation_duration_seconds | generation_status | answer_is_fallback |
|---|---:|---:|---:|---|---|
| rag_definition | 16.52 | 0.24 | 16.27 | completed | false |
| qdrant_usage | 32.62 | 0.24 | 32.38 | completed | false |
| langchain_usage | 24.16 | 0.28 | 23.87 | completed | false |

汇总：

- 测试问题数：3
- Top-K：7
- 平均耗时：24.43 秒
- 最大耗时：32.62 秒
- 最小耗时：16.52 秒

### 历史 Top-K 对比：top_k = 7

| case_id | total_duration_seconds | retrieval_duration_seconds | generation_duration_seconds |
|---|---:|---:|---:|
| rag_definition | 23.03 | 1.15 | 21.87 |
| qdrant_usage | 29.08 | 0.24 | 28.83 |
| langchain_usage | 26.29 | 0.28 | 26.00 |

汇总：

- 测试问题数：3
- Top-K：7
- 平均耗时：26.13 秒
- 最大耗时：29.08 秒
- 最小耗时：23.03 秒

### 历史 Top-K 对比：top_k = 3

| case_id | total_duration_seconds | retrieval_duration_seconds | generation_duration_seconds |
|---|---:|---:|---:|
| rag_definition | 34.66 | 1.98 | 32.67 |
| qdrant_usage | 18.40 | 0.24 | 18.15 |
| langchain_usage | 22.08 | 0.55 | 21.52 |

汇总：

- 测试问题数：3
- Top-K：3
- 平均耗时：25.05 秒
- 最大耗时：34.66 秒
- 最小耗时：18.40 秒

## 结论

当前有效模型基线对用户侧问答接口来说偏慢，不能用于宣称“平均 2 秒内响应”。

有效结果显示主要耗时来自 LLM 生成阶段，而不是向量检索阶段。使用 `kimi-k2.5` 时，向量检索在当前样本中均低于 1 秒，但 LLM 生成在 16 秒到 33 秒之间。

将 Top-K 从 7 降到 3 没有带来稳定、明确的延迟优化。平均总耗时从 26.13 秒降到 25.05 秒，但 `rag_definition` 这个 case 反而从 23.03 秒上升到 34.66 秒。

因此，下一步优化不应优先继续调整检索参数，而应优先验证生成侧变量，例如：

- 更快的 LLM 模型
- 更短的 Prompt
- 更严格的输出长度限制
- 更小的上下文 token budget

## 简历表述边界

当前可以安全表述为：

`设计 RAG latency benchmark，对完整问答链路进行分段耗时统计，并定位主要瓶颈来自 LLM 生成阶段。`

当前不应表述为：

`平均响应时延控制在 2 秒内。`
