from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from src import config
from src.clients import get_client

def build_prompt() ->ChatPromptTemplate:
    return ChatPromptTemplate(
        [
            ("system" , config.DEFAULT_SYSTEM_PROMPT + "\n\nContext: \n{context}"),
            ("human" , "{question}")
        ]
    )

def format_context(documents: list[Document]) -> str:
    if not documents:
        return ""

    parts : list[str] = []

    for index , document in enumerate(documents , start=1):
        source = document.metadata.get("source" , "unknown")

        formatted_text = (
            f"[Document {index}]\n"
            f"Source: {source}\n"
            f"Content: {document.page_content}"
        )

        parts.append(formatted_text)
    return "\n".join(parts)


def generate_answer(question : str ,context : str) -> str:
    if not context.strip():
        return config.FALLBACK_ANSWER

    prompt = build_prompt()

    client = get_client()

    chain = prompt | client | StrOutputParser()

    return chain.invoke(
        {
            "system_prompt": config.DEFAULT_SYSTEM_PROMPT,
            "context": context,
            "question": question,
        }
    )




