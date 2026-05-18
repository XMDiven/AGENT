from langchain_core.prompts import ChatPromptTemplate

from rag_app.config import config


QA_PROMPT_V1 = (
    "Question:\n{question}\n\n"
    "Context:\n{context}\n\n"
    "Answer in Chinese using only the provided Context.\n"
    "Give a direct answer first, then key evidence.\n"
    "Use only citation markers like [1] or [2].\n"
    "Do not include file paths, file names, URLs, or local paths in the answer.\n"
    "Do not include source, section_path, or page_content labels in the answer.\n"
    "If the Context is not enough to answer, say you do not know."
)

QA_PROMPT_V2 = (
    "Question:\n{question}\n\n"
    "Context:\n{context}\n\n"
    "Answer in Chinese using only the provided Context.\n"
    "Use the following exact structure:\n"
    "Direct answer:\n"
    "- Provide a concise answer in 1-3 sentences.\n\n"
    "Key evidence:\n"
    "- Provide 2-5 bullet points.\n"
    "- Each bullet must include a citation marker like [1] or [2].\n\n"
    "Limitations:\n"
    "- If the Context is not enough, explain what is missing.\n"
    "- If the Context is enough, write: No major limitation from the provided context.\n\n"
    "Do not include file paths, file names, URLs, or local paths in the answer.\n"
    "Do not include source, section_path, or page_content labels in the answer."
)

QA_PROMPTS = {
    "qa_prompt_v1": QA_PROMPT_V1,
    "qa_prompt_v2": QA_PROMPT_V2,
}


def get_qa_prompt() -> ChatPromptTemplate:
    prompt_template = QA_PROMPTS.get(config.QA_PROMPT_VERSION)

    if prompt_template is None:
        raise ValueError(
            f"Unsupported QA_PROMPT_VERSION: {config.QA_PROMPT_VERSION}"
        )

    return ChatPromptTemplate.from_messages(
        [
            ("system", config.DEFAULT_SYSTEM_PROMPT),
            ("human", prompt_template),
        ]
    )
