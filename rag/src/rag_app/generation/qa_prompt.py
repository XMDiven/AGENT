from langchain_core.prompts import ChatPromptTemplate

from rag_app.config import config

QA_PROMPT_VERSION = "qa_prompt_v1"

def get_qa_prompt() -> ChatPromptTemplate:

    return ChatPromptTemplate.from_messages(
        [
            ("system", config.DEFAULT_SYSTEM_PROMPT),
            (
                "human",
                "Question:\n{question}\n\n"
                "Context:\n{context}\n\n"
                "Answer in Chinese using only the provided Context.\n"
                "Give a direct answer first, then key evidence.\n"
                "Use only citation markers like [1] or [2].\n"
                "Do not include file paths, file names, URLs, or local paths in the answer.\n"
                "Do not include source, section_path, or page_content labels in the answer.\n"
                "If the Context is not enough to answer, say you do not know.",
            ),
        ]
    )
