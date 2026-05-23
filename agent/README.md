# Agent

`agent` 是建立在 `rag` 子项目之上的轻量 Agent 编排层。它当前不实现完整 ReAct、多 Agent 协作或通用工具平台，而是先把最小可验证链路做清楚：

```text
analyze_question -> plan_tool -> execute_tool -> build AgentState -> return result with trace
```

## 当前能力

- 调用 RAG 的 `analyze_query()` 判断问题是否需要检索
- 根据 `question_type` 选择 `retrieval_tool`、`summary_tool` 或 `fallback_tool`
- 通过 `executor` 执行工具
- `retrieval_tool` 会调用 `rag_app.services.ask_service.ask_question`
- `summary_tool` 会对用户输入文本执行本地确定性摘要
- 返回结构化 `AgentRunResult`
- 返回 Agent 层 trace，记录分析、规划和执行步骤
- 使用 `AgentState` 保存 question、analysis、plan、tool_result 和 trace，明确 Agent 内部状态流转
- 当 `retrieval_tool` 执行失败时，最多尝试 3 次，并返回结构化失败结果和 attempts 记录
- 通过 FastAPI 暴露 `POST /agent/run` 接口
- 提供 `GET /health` 健康检查接口

## 模块结构

```text
src/agent_app/
  app/
    main.py            # FastAPI 应用入口
    routers/health.py  # GET /health 健康检查接口
    routers/run.py     # POST /agent/run 接口
  schemas/run.py    # Agent API 请求和响应结构
  orchestration/
    planner.py       # 根据问题分析结果选择工具
    executor.py      # 执行工具并包装 ToolResult
    state.py         # Agent 内部状态对象
  tools/
    registry.py      # 工具注册表
    retrieval.py     # 调用 RAG 问答服务的工具适配层
    summary.py       # 本地摘要工具
  service.py         # Agent 对外统一入口 run_agent(question)
```

目录边界：

- `app/` 只处理 HTTP 入口。
- `schemas/` 只放 API 请求和响应结构。
- `service.py` 负责串起一次 Agent run。
- `orchestration/` 放规划、执行和状态流转。
- `tools/` 放工具注册表和具体工具适配层。

## 执行流程

`run_agent(question)` 是当前 Agent 的统一入口：

```python
from agent_app.service import run_agent

result = run_agent("What is RAG?")
```

返回对象包含：

- `plan`: 工具选择结果
- `tool_result`: 工具执行结果
- `trace`: Agent 层执行轨迹

## 工具规划策略

当前 planner 是规则式规划，不调用 LLM。它根据 RAG `query_analyzer` 返回的 `question_type` 选择工具：

| question_type | tool | 说明 |
| --- | --- | --- |
| `empty` | `fallback_tool` | 空问题不执行检索 |
| `summary` | `summary_tool` | 对用户输入文本做本地摘要 |
| `general` | `retrieval_tool` | 使用 RAG 知识库检索回答 |
| `comparison` | `retrieval_tool` | 使用 RAG 知识库检索后回答比较类问题 |

普通知识问题成功路径示例：

```json
[
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
```

`retrieval_tool` 调用 RAG，可能遇到向量库、LLM 或网络类临时失败，因此 executor 会最多尝试 3 次。工具失败时，`tool_result.status` 会变为 `failed`，并返回错误类型、错误信息和每次尝试记录：

```json
{
  "tool_name": "retrieval_tool",
  "status": "failed",
  "output": {
    "error_type": "RuntimeError",
    "error": "rag unavailable"
  },
  "attempts": [
    {
      "attempt": 1,
      "status": "failed",
      "error_type": "RuntimeError",
      "error": "rag unavailable"
    },
    {
      "attempt": 2,
      "status": "failed",
      "error_type": "RuntimeError",
      "error": "rag unavailable"
    },
    {
      "attempt": 3,
      "status": "failed",
      "error_type": "RuntimeError",
      "error": "rag unavailable"
    }
  ]
}
```

总结类问题会走 `summary_tool`：

```json
[
  {
    "step": "analyze_question",
    "status": "completed",
    "detail": {
      "needs_retrieval": true,
      "question_type": "summary",
      "reason": "summary question, use retrieval"
    }
  },
  {
    "step": "plan_tool",
    "status": "completed",
    "detail": {
      "tool_name": "summary_tool",
      "reason": "question asks for summarization"
    }
  },
  {
    "step": "execute_tool",
    "status": "success",
    "detail": {
      "tool_name": "summary_tool",
      "attempts": [
        {
          "attempt": 1,
          "status": "success"
        }
      ]
    }
  }
]
```

## 和 RAG 的关系

Agent trace 记录上层编排过程：

```text
Agent 为什么选择工具、执行了哪个工具、执行状态是什么
```

RAG trace 记录工具内部过程：

```text
query analysis、retrieval planning、retrieve、generate answer
```

因此，RAG 是 Agent 当前调用的第一个真实工具，Agent 负责上层决策和执行状态追踪。

## 运行测试

```bash
cd agent
conda run -n AI_DEV pytest tests/ -q
```

## CLI 演示

可以通过最小 CLI 入口运行 Agent 编排流程：

```bash
cd agent
conda run -n AI_DEV python -m agent_app.scripts.run_agent ""
```

空字符串会走 `fallback_tool`，适合验证 CLI 和 Agent trace 输出。普通知识问题会走 `retrieval_tool`，可能触发 RAG 检索和 LLM 调用。

总结类问题会走 `summary_tool`：

```bash
conda run -n AI_DEV python -m agent_app.scripts.run_agent "请总结 LangChain 的用途"
```

响应中的 `tool_result` 会包含：

```json
{
  "tool_name": "summary_tool",
  "status": "success",
  "output": {
    "summary": "请总结 LangChain 的用途"
  }
}
```

## FastAPI 接口

启动 Agent API：

```bash
cd agent
conda run -n AI_DEV uvicorn agent_app.app.main:app --reload
```

调用 `POST /agent/run`：

```bash
curl -X POST http://127.0.0.1:8000/agent/run \
  -H "Content-Type: application/json" \
  -d '{"question": ""}'
```

空字符串会走 `fallback_tool`，适合验证 API、Agent trace 和响应结构。普通知识问题会走 `retrieval_tool`，可能触发 RAG 检索和 LLM 调用。

调用总结工具：

```bash
curl -X POST http://127.0.0.1:8000/agent/run \
  -H "Content-Type: application/json" \
  -d '{"question": "请总结 LangChain 的用途"}'
```

健康检查接口：

```bash
curl http://127.0.0.1:8000/health
```

返回：

```json
{
  "status": "ok",
  "service": "agent"
}
```

## 当前边界

当前 `agent` 是轻量编排层，不是完整 Agent 平台。它还没有实现：

- LLM planner
- ReAct 循环
- 多轮工具调用
- LLM 摘要工具
- 网络搜索工具
- 多 Agent 协作

这些能力应在现有工具注册、规划、执行、trace 和失败处理稳定后再逐步扩展。
