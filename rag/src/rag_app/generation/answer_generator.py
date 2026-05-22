from collections.abc import Iterator

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate


def generate_answer(
    question: str,
    context: str,
    llm: BaseChatModel,
    prompt: ChatPromptTemplate,
) -> str:
    chain = prompt | llm | StrOutputParser()
    return chain.invoke(
        {"question": question, "context": context}
    )


def stream_answer(
    question: str,
    context: str,
    llm: BaseChatModel,
    prompt: ChatPromptTemplate,
) -> Iterator[str]:
    chain = prompt | llm | StrOutputParser()
    for chunk in chain.stream(
        {"question": question, "context": context}
    ):
        if chunk:
            yield chunk
