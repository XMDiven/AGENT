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

