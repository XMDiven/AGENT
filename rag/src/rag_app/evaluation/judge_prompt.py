from langchain_core.prompts import ChatPromptTemplate


ANSWER_JUDGE_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are an answer quality judge for a RAG system.

Evaluate the answer only based on the provided retrieved evidence.
Do not use outside knowledge.

Score each dimension from 1 to 5:
- relevance_score: whether the answer directly answers the question
- completeness_score: whether the answer covers the key points
- groundedness_score: whether the answer is supported by the evidence
- format_score: whether the answer is clear and well formatted

Return only valid JSON with these fields:
relevance_score, completeness_score, groundedness_score, format_score,
overall_pass, feedback.

Set overall_pass to true only when every score is 4 or higher.
Otherwise set overall_pass to false.
""".strip(),
        ),
        (
            "human",
            """
Question:
{question}

Answer:
{answer}

Retrieved evidence:
{evidence}
""".strip(),
        ),
    ]
)


def get_answer_judge_prompt() -> ChatPromptTemplate:
    return ANSWER_JUDGE_PROMPT
