from dataclasses import dataclass


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    description: str

AVAILABLE_TOOLS: dict[str, ToolDefinition] = {
    "retrieval_tool": ToolDefinition(
        name="retrieval_tool",
        description="Retrieve relevant documents from the RAG knowledge base.",
    ),
    "summary_tool": ToolDefinition(
        name="summary_tool",
        description="Summarize user-provided text.",
    ),
    "fallback_tool": ToolDefinition(
        name="fallback_tool",
        description="Return a fallback response when no tool should run.",
    ),
}


def list_tools() -> list[ToolDefinition]:
    return list(AVAILABLE_TOOLS.values())


def get_tool(name: str) -> ToolDefinition:
    tool = AVAILABLE_TOOLS.get(name)
    if tool is None:
        raise ValueError(f"Unknown tool: {name}")

    return tool
