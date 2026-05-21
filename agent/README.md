# Agent

`agent` 是建立在 `rag` 子项目之上的轻量 Agent 编排层。它当前不实现完整 ReAct、多 Agent 协作或通用工具平台，而是先把最小可验证链路做清楚：

```text
analyze_question -> plan_tool -> execute_tool -> return result with trace
```

## 当前能力

- 调用 RAG 的 `analyze_query()` 判断问题是否需要检索
- 根据 `needs_retrieval` 选择 `retrieval_tool` 或 `fallback_tool`
- 通过 `executor` 执行工具
- `retrieval_tool` 会调用 `rag_app.services.ask_service.ask_question`
- 返回结构化 `AgentRunResult`
- 返回 Agent 层 trace，记录分析、规划和执行步骤
- 当 retrieval tool 执行失败时，返回结构化失败结果

## 模块结构

```text
src/agent_app/
  tools.py           # 工具注册表
  planner.py         # 根据问题分析结果选择工具
  executor.py        # 执行工具并包装 ToolResult
  retrieval_tool.py  # 调用 RAG 问答服务的工具适配层
  service.py         # Agent 对外统一入口 run_agent(question)
```

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

成功路径示例：

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
      "tool_name": "retrieval_tool"
    }
  }
]
```

工具失败时，`tool_result.status` 会变为 `failed`，并返回错误类型和错误信息：

```json
{
  "error_type": "RuntimeError",
  "error": "rag unavailable"
}
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

## 当前边界

当前 `agent` 是轻量编排层，不是完整 Agent 平台。它还没有实现：

- LLM planner
- ReAct 循环
- 多轮工具调用
- 网络搜索工具
- 多 Agent 协作
- FastAPI Agent endpoint

这些能力应在现有工具注册、规划、执行、trace 和失败处理稳定后再逐步扩展。
