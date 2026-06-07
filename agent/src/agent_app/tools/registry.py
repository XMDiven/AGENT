from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    description: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]


AVAILABLE_TOOLS: dict[str, ToolDefinition] = {
    "retrieval_tool": ToolDefinition(
        name="retrieval_tool",
        description="Retrieve relevant documents from the RAG knowledge base.",
        input_schema={
            "type": "object",
            "required": ["question"],
            "properties": {
                "question": {
                    "type": "string",
                    "description": "User question to answer with RAG retrieval.",
                },
            },
        },
        output_schema={
            "type": "object",
            "required": ["answer", "sources"],
            "properties": {
                "answer": {
                    "type": "string",
                    "description": (
                        "Generated answer grounded in retrieved sources."
                    ),
                },
                "sources": {
                    "type": "array",
                    "description": (
                        "Retrieved source references used by the answer."
                    ),
                },
                "trace": {
                    "type": "array",
                    "description": "RAG execution trace.",
                },
            },
        },
    ),
    "summary_tool": ToolDefinition(
        name="summary_tool",
        description="Summarize user-provided text.",
        input_schema={
            "type": "object",
            "required": ["text"],
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Text to summarize.",
                },
            },
        },
        output_schema={
            "type": "object",
            "required": ["summary"],
            "properties": {
                "summary": {
                    "type": "string",
                    "description": "Concise LLM-generated summary.",
                },
            },
        },
    ),
    "question_decompose_tool": ToolDefinition(
        name="question_decompose_tool",
        description=(
            "Decompose comparison or multi-part questions into sub-questions "
            "and aggregate retrieval results."
        ),
        input_schema={
            "type": "object",
            "required": ["question"],
            "properties": {
                "question": {
                    "type": "string",
                    "description": (
                        "Comparison or multi-part question to decompose."
                    ),
                },
            },
        },
        output_schema={
            "type": "object",
            "required": [
                "answer",
                "sources",
                "sub_questions",
                "sub_results",
            ],
            "properties": {
                "answer": {
                    "type": "string",
                    "description": (
                        "Aggregated answer built from sub-question results."
                    ),
                },
                "sources": {
                    "type": "array",
                    "description": (
                        "Combined sources from all sub-question results."
                    ),
                },
                "sub_questions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Generated sub-questions.",
                },
                "sub_results": {
                    "type": "array",
                    "description": "Per-sub-question retrieval results.",
                },
                "reason": {
                    "type": "string",
                    "description": "Reason for decomposition.",
                },
                "decomposition_strategy": {
                    "type": "string",
                    "description": "Strategy used to split the question.",
                },
            },
        },
    ),
    "fallback_tool": ToolDefinition(
        name="fallback_tool",
        description="Return a fallback response when no tool should run.",
        input_schema={
            "type": "object",
            "properties": {},
        },
        output_schema={
            "type": "object",
            "required": ["answer", "sources"],
            "properties": {
                "answer": {
                    "type": "string",
                    "description": "Fallback answer.",
                },
                "sources": {
                    "type": "array",
                    "description": "Empty source list.",
                },
            },
        },
    ),
}


def list_tools() -> list[ToolDefinition]:
    return list(AVAILABLE_TOOLS.values())


def get_tool(name: str) -> ToolDefinition:
    tool = AVAILABLE_TOOLS.get(name)
    if tool is None:
        raise ValueError(f"Unknown tool: {name}")

    return tool
