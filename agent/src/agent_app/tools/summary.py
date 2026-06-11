from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from agent_app.prompts import SUMMARY_SYSTEM_PROMPT
from rag_app.infrastructure.llm_client import get_client


def extract_message_content(message: AIMessage) -> str:
    content = getattr(message, "content", "")

    if isinstance(content, str):
        return content.strip()

    return str(content).strip()


def run_summary_tool(
    text: str,
    llm: ChatOpenAI | None = None,
    max_chars: int = 600,
) -> dict[str, str]:
    normalized_text = " ".join(text.split())

    if not normalized_text:
        return {
            "summary": "No text provided for summarization.",
        }

    client = llm or get_client()
    message = client.invoke(
        [
            SystemMessage(content=SUMMARY_SYSTEM_PROMPT),
            HumanMessage(content=normalized_text),
        ]
    )

    summary = extract_message_content(message)

    if not summary:
        return {
            "summary": "The model returned an empty summary.",
        }

    if len(summary) > max_chars:
        summary = summary[:max_chars].rstrip() + "..."

    return {
        "summary": summary,
    }
