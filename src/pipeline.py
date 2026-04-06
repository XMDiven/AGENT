from src.generate import format_context, generate_answer
from src.retrieve import retrieve_documents


def ask(question: str) -> str:
    documents = retrieve_documents(question)
    context = format_context(documents)
    answer = generate_answer(question, context)
    return answer
