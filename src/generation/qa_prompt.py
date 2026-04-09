from langchain_core.prompts import ChatPromptTemplate

from config import config

def get_qa_prompt() -> ChatPromptTemplate:
    """Return the QA prompt template."""
    return ChatPromptTemplate.from_messages(
        [
            ("system", config.DEFAULT_SYSTEM_PROMPT),
            (
                "human",
                "Question:\n{question}\n\nContext:\n{context}\n\n"
                "Answer in Chinese. Give a direct answer first, then key evidence, then citations.",
            ),
        ]
    )
